#!/usr/bin/env python3
"""
FreeChorder - Software CharaChorder for macOS
Main CLI entry point
"""

import click
import sys
import os
import builtins
from pathlib import Path
from datetime import datetime

from freechorder.core.chord_manager import ChordManager, ChordConflictError
from freechorder.core.impulse_handler import ImpulseHandler
from freechorder.karabiner.config_generator import KarabinerBridge
from freechorder.utils.config import Config
from freechorder.utils.permissions import check_accessibility_permissions, show_accessibility_instructions, open_accessibility_settings
from freechorder.cli.interactive_add import InteractiveChordAdder


@click.group()
@click.version_option(version='0.1.0')
@click.pass_context
def cli(ctx):
    """FreeChorder - Software CharaChorder for macOS
    
    Manage keyboard chords using Karabiner-Elements as the backend.
    """
    # Initialize configuration
    config = Config()
    chord_manager = ChordManager(config.chord_file)
    karabiner = KarabinerBridge(config.karabiner_config_path, config.chord_timeout_ms, config.sensitivity_map)
    
    # Store in context for subcommands
    ctx.ensure_object(dict)
    ctx.obj['config'] = config
    ctx.obj['chord_manager'] = chord_manager
    ctx.obj['karabiner'] = karabiner


@cli.command()
@click.argument('input_keys', required=False)
@click.argument('output_text', required=False)
@click.option('--category', help='Category for the chord')
@click.option('--tags', help='Comma-separated tags')
@click.option('--batch', '-b', help='Add multiple chords from a file (one per line: "keys,output")')
@click.option('--no-confirm', is_flag=True, help='Skip confirmation prompt')
@click.pass_context
def add(ctx, input_keys, output_text, category, tags, batch, no_confirm):
    """Add a new chord with interactive prompts and confirmation.
    
    INPUT_KEYS: Keys to press simultaneously (e.g., "asd" or "a+s+d") [optional - will prompt if not provided]
    OUTPUT_TEXT: Text to output when chord is pressed [optional - will prompt if not provided]
    
    Examples:
      fc add              # Interactive mode with prompts
      fc add "asd" "and"  # Quick add with confirmation
      fc add "asd" "and" --no-confirm  # Quick add without confirmation
      fc add --batch chords.txt  # Add multiple chords from file
    """
    chord_manager = ctx.obj['chord_manager']
    karabiner = ctx.obj['karabiner']
    
    # Create interactive adder
    adder = InteractiveChordAdder(chord_manager, karabiner)
    
    try:
        if batch:
            # Batch mode from file
            try:
                with open(batch, 'r') as f:
                    lines = [line.strip() for line in f if line.strip() and not line.startswith('#')]
                
                chord_pairs = []
                for line in lines:
                    parts = line.split(',', 1)
                    if len(parts) == 2:
                        chord_pairs.append((parts[0].strip(), parts[1].strip()))
                
                adder.add_batch(chord_pairs, category=category)
            except FileNotFoundError:
                click.echo(f"❌ Error: File '{batch}' not found", err=True)
                ctx.exit(1)
        else:
            # Single chord addition with interactive prompts
            adder.add_interactive(
                input_keys=input_keys,
                output_text=output_text,
                category=category,
                skip_confirm=no_confirm
            )
        
    except KeyboardInterrupt:
        click.echo("\n\n✗ Cancelled by user")
        ctx.exit(0)
    except Exception as e:
        click.echo(f"\n❌ Unexpected error: {str(e)}", err=True)
        ctx.exit(1)


@cli.command()
@click.argument('chord_input', required=False)
@click.option('--output', help='Remove by output text')
@click.pass_context
def remove(ctx, chord_input, output):
    """Remove a chord.
    
    CHORD_INPUT: Input keys of the chord to remove (e.g., "asd")
    """
    chord_manager = ctx.obj['chord_manager']
    karabiner = ctx.obj['karabiner']
    
    try:
        if chord_input:
            # Remove by input
            keys = chord_input.replace('+', '').lower()
            keys_list = builtins.list(keys)
            removed = chord_manager.remove_chord_by_input(keys_list)
        elif output:
            # Remove by output
            removed = chord_manager.remove_chord_by_output(output)
        else:
            click.echo("Error: Provide either chord input or --output", err=True)
            ctx.exit(1)
        
        if removed:
            # Update Karabiner configuration
            all_chords = chord_manager.get_all_chords()
            karabiner.update_all_chords(all_chords)
            
            click.echo(f"✓ Removed chord: {'+'.join(removed.input_keys)} → {removed.output_text}")
        else:
            click.echo("✗ Chord not found", err=True)
            ctx.exit(1)
            
    except Exception as e:
        click.echo(f"✗ Error: {str(e)}", err=True)
        ctx.exit(1)


@cli.command()
@click.option('--category', help='Filter by category')
@click.option('--sort', type=click.Choice(['input', 'output', 'usage', 'created']), 
              default='created', help='Sort order')
@click.pass_context
def list(ctx, category, sort):
    """List all chords."""
    chord_manager = ctx.obj['chord_manager']
    
    try:
        chords = chord_manager.get_all_chords()
        
        # Filter by category if specified
        if category:
            chords = [c for c in chords if c.category == category]
        
        # Sort chords
        if sort == 'input':
            chords.sort(key=lambda c: ''.join(c.input_keys))
        elif sort == 'output':
            chords.sort(key=lambda c: c.output_text)
        elif sort == 'usage':
            chords.sort(key=lambda c: c.usage_count, reverse=True)
        # 'created' is default, already sorted
        
        if not chords:
            click.echo("No chords found.")
            return
        
        # Display chords
        click.echo(f"\nTotal chords: {len(chords)}\n")
        
        for chord in chords:
            input_str = '+'.join(chord.input_keys)
            category_str = f" [{chord.category}]" if chord.category else ""
            usage_str = f" (used {chord.usage_count}x)" if chord.usage_count > 0 else ""
            
            click.echo(f"  {input_str} → {chord.output_text}{category_str}{usage_str}")
        
        click.echo()
        
    except Exception as e:
        click.echo(f"✗ Error: {str(e)}", err=True)
        ctx.exit(1)


@cli.command()
@click.argument('search_term')
@click.option('--input', 'search_type', flag_value='input', help='Search only in input keys')
@click.option('--output', 'search_type', flag_value='output', help='Search only in output text')
@click.pass_context
def search(ctx, search_term, search_type):
    """Search for chords."""
    chord_manager = ctx.obj['chord_manager']
    
    try:
        # Default to searching both
        if not search_type:
            search_type = 'all'
        
        results = chord_manager.search_chords(search_term, search_type)
        
        if not results:
            click.echo("No chords found.")
            return
        
        # Display results
        click.echo(f"\nFound {len(results)} chord(s):\n")
        
        for chord in results:
            input_str = '+'.join(chord.input_keys)
            category_str = f" [{chord.category}]" if chord.category else ""
            
            click.echo(f"  {input_str} → {chord.output_text}{category_str}")
        
        click.echo()
        
    except Exception as e:
        click.echo(f"✗ Error: {str(e)}", err=True)
        ctx.exit(1)


@cli.command()
@click.option('--detailed', '-d', is_flag=True, help='Show detailed breakdown')
@click.pass_context
def stats(ctx, detailed):
    """Show chord statistics and analytics."""
    chord_manager = ctx.obj['chord_manager']
    
    try:
        stats = chord_manager.get_statistics()
        all_chords = chord_manager.get_all_chords()
        
        # Calculate additional statistics
        chord_lengths = {}
        categories_count = {}
        oldest_chord = None
        newest_chord = None
        
        for chord in all_chords:
            # Length distribution
            length = len([k for k in chord.input_keys if k not in ['cmd', 'shift', 'option', 'control']])
            chord_lengths[length] = chord_lengths.get(length, 0) + 1
            
            # Category distribution
            cat = chord.category or "Uncategorized"
            categories_count[cat] = categories_count.get(cat, 0) + 1
            
            # Oldest/newest
            if not oldest_chord or chord.created_at < oldest_chord.created_at:
                oldest_chord = chord
            if not newest_chord or chord.created_at > newest_chord.created_at:
                newest_chord = chord
        
        # Display statistics
        click.echo("\n" + "=" * 60)
        click.echo("📊 FreeChorder Statistics".center(60))
        click.echo("=" * 60)
        
        # Basic stats
        click.echo(f"\n📝 Overview:")
        click.echo(f"   Total chords: {stats['total_chords']}")
        click.echo(f"   Unique categories: {stats['categories']}")
        
        if oldest_chord:
            click.echo(f"   Oldest chord: {oldest_chord.created_at.strftime('%Y-%m-%d')}")
        if newest_chord:
            click.echo(f"   Newest chord: {newest_chord.created_at.strftime('%Y-%m-%d')}")
        
        # Chord length distribution
        if chord_lengths:
            click.echo(f"\n🎹 Chord Length Distribution:")
            for length in sorted(chord_lengths.keys()):
                count = chord_lengths[length]
                percentage = (count / stats['total_chords']) * 100
                bar = "█" * int(percentage / 5)  # Scale bar
                click.echo(f"   {length} keys: {count:3d} chords {bar} ({percentage:.1f}%)")
        
        # Category breakdown
        if categories_count:
            click.echo(f"\n📂 Category Breakdown:")
            for cat, count in sorted(categories_count.items(), key=lambda x: -x[1])[:5]:
                percentage = (count / stats['total_chords']) * 100
                bar = "█" * int(percentage / 5)
                click.echo(f"   {cat}: {count:3d} chords {bar} ({percentage:.1f}%)")
        
        # Most recent chords
        if all_chords:
            click.echo(f"\n🆕 Recently Added (last 5):")
            recent = sorted(all_chords, key=lambda c: c.created_at, reverse=True)[:5]
            for chord in recent:
                input_str = '+'.join(chord.input_keys)
                age_days = (datetime.now() - chord.created_at).days
                age_str = f"{age_days}d ago" if age_days > 0 else "today"
                click.echo(f"   {input_str} → '{chord.output_text}' ({age_str})")
        
        # Usage statistics (if any usage data exists)
        if stats['total_usage'] > 0:
            click.echo(f"\n🔥 Most Used Chords:")
            for chord in stats['most_used'][:5]:
                input_str = '+'.join(chord.input_keys)
                click.echo(f"   {input_str} → '{chord.output_text}' ({chord.usage_count}x)")
        else:
            click.echo(f"\n💡 Tip: Usage tracking not yet implemented")
            click.echo(f"   Future feature: Track which chords you use most")
        
        # Detailed breakdown
        if detailed:
            click.echo(f"\n🔍 Detailed Breakdown:")
            click.echo(f"\n   All Chords by Category:")
            for cat in sorted(categories_count.keys()):
                click.echo(f"\n   {cat} ({categories_count[cat]} chords):")
                cat_chords = [c for c in all_chords if (c.category or "Uncategorized") == cat]
                for chord in sorted(cat_chords, key=lambda c: len(c.input_keys), reverse=True)[:10]:
                    input_str = '+'.join(chord.input_keys)
                    click.echo(f"      {input_str} → '{chord.output_text}'")
        
        click.echo("\n" + "=" * 60)
        click.echo(f"💡 Use 'fc stats --detailed' for full breakdown")
        click.echo("=" * 60 + "\n")
        
    except Exception as e:
        click.echo(f"✗ Error: {str(e)}", err=True)
        ctx.exit(1)


@cli.command()
@click.pass_context
def permissions(ctx):
    """Check and fix accessibility permissions for impulse mode."""
    click.echo("🔍 Checking accessibility permissions for FreeChorder...\n")
    
    if check_accessibility_permissions():
        click.echo("✅ Accessibility permissions are properly configured!")
        click.echo("\nYou can now use 'freechorder impulse' to create chords on-the-fly.")
    else:
        click.echo("❌ Accessibility permissions not granted!")
        show_accessibility_instructions()
        
        if click.confirm("\n🔧 Would you like to open System Settings now?", default=True):
            open_accessibility_settings()
            click.echo("\n✅ After granting permissions:")
            click.echo("1. Restart your terminal")
            click.echo("2. Run 'freechorder impulse' to start creating chords")
        else:
            click.echo("\n💡 Grant permissions manually following the instructions above.")
            click.echo("Then restart your terminal and try again.")


@cli.command()
@click.option('--chord-timeout', type=int, help='Set chord detection timeout in milliseconds (default: 100ms)')
@click.option('--show', is_flag=True, help='Show current configuration')
@click.pass_context
def config(ctx, chord_timeout, show):
    """Configure FreeChorder settings."""
    config_obj = ctx.obj['config']
    
    if show:
        click.echo("\nCurrent FreeChorder Configuration:")
        click.echo("=" * 40)
        click.echo(f"Chord Detection Timeout: {config_obj.chord_timeout_ms}ms")
        click.echo(f"Minimum Chord Size: {config_obj.min_chord_size} keys")
        click.echo(f"Chord Storage: {config_obj.chord_file}")
        click.echo(f"Karabiner Profile: {config_obj.karabiner_profile_name}")
        click.echo()
        return
    
    if chord_timeout is not None:
        if chord_timeout < 50:
            click.echo("⚠️  Warning: Very low timeout values may make chord detection difficult.")
            if not click.confirm(f"Set chord timeout to {chord_timeout}ms?"):
                return
        elif chord_timeout > 500:
            click.echo("⚠️  Warning: High timeout values may make typing feel sluggish.")
            if not click.confirm(f"Set chord timeout to {chord_timeout}ms?"):
                return
        
        config_obj.set('impulse.chord_timeout_ms', chord_timeout)
        click.echo(f"✓ Chord detection timeout set to {chord_timeout}ms")
        
        # Update all existing chords in Karabiner with new timing
        click.echo("\n🔄 Updating all existing chords with new sensitivity...")
        chord_manager = ctx.obj['chord_manager']
        karabiner = ctx.obj['karabiner']
        
        # Reinitialize karabiner with new timeout
        karabiner.chord_timeout_ms = chord_timeout
        
        # Regenerate all chord rules
        all_chords = chord_manager.get_all_chords()
        if all_chords:
            karabiner.update_all_chords(all_chords)
            click.echo(f"✓ Updated {len(all_chords)} chords in Karabiner with {chord_timeout}ms timing")
        else:
            click.echo("ℹ️  No existing chords to update")
        
        click.echo("\n✨ All chords now use the new sensitivity setting!")
    else:
        click.echo("No configuration changes made.")
        click.echo("Use --show to see current settings or --chord-timeout to set timeout.")


@cli.command()
@click.pass_context
def sync(ctx):
    """Sync quick impulse chords to Karabiner."""
    import json
    from pathlib import Path
    
    chord_manager = ctx.obj['chord_manager']
    karabiner = ctx.obj['karabiner']
    
    cache_file = Path.home() / '.config' / 'freechorder' / '.quick_chords_cache'
    
    if not cache_file.exists():
        click.echo("No quick chords to sync.")
        return
    
    synced_count = 0
    try:
        with open(cache_file, 'r') as f:
            lines = f.readlines()
        
        for line in lines:
            if line.strip():
                try:
                    chord_data = json.loads(line)
                    chord_manager.add_chord(
                        input_keys=chord_data['input_keys'],
                        output_text=chord_data['output_text'],
                        category=chord_data.get('category', 'quick_impulse')
                    )
                    synced_count += 1
                except ChordConflictError:
                    # Skip duplicates silently
                    pass
                except Exception as e:
                    click.echo(f"Failed to sync chord: {e}")
        
        if synced_count > 0:
            # Update Karabiner
            all_chords = chord_manager.get_all_chords()
            karabiner.update_all_chords(all_chords)
            
            # Clear cache
            cache_file.unlink()
            
            click.echo(f"✓ Synced {synced_count} quick chords to Karabiner!")
        else:
            click.echo("No valid chords to sync.")
            
    except Exception as e:
        click.echo(f"✗ Error syncing chords: {str(e)}", err=True)
        ctx.exit(1)


@cli.command()
@click.pass_context
def activate(ctx):
    """Activate the FreeChorder profile in Karabiner-Elements."""
    karabiner = ctx.obj['karabiner']
    
    try:
        karabiner.activate_freechorder_profile()
        click.echo("✓ FreeChorder profile activated in Karabiner-Elements!")
        click.echo("Your chords are now active and ready to use.")
    except Exception as e:
        click.echo(f"✗ Error activating profile: {str(e)}", err=True)
        ctx.exit(1)


@cli.command()
@click.pass_context
def refresh(ctx):
    """Refresh all chords in Karabiner with current settings (including dynamic sensitivity)."""
    chord_manager = ctx.obj['chord_manager']
    karabiner = ctx.obj['karabiner']
    config_obj = ctx.obj['config']
    
    try:
        # Update karabiner with latest config
        karabiner.chord_timeout_ms = config_obj.chord_timeout_ms
        karabiner.sensitivity_map = config_obj.sensitivity_map
        
        # Regenerate all chord rules
        all_chords = chord_manager.get_all_chords()
        if all_chords:
            click.echo("🔄 Refreshing all chords with dynamic sensitivity...")
            click.echo(f"\n📊 Sensitivity settings:")
            click.echo(f"   • 2 keys: {karabiner.sensitivity_map[2]}ms (strict)")
            click.echo(f"   • 3 keys: {karabiner.sensitivity_map[3]}ms (moderate)")
            click.echo(f"   • 4 keys: {karabiner.sensitivity_map[4]}ms (default)")
            click.echo(f"   • 5+ keys: {karabiner.sensitivity_map[5]}ms (relaxed)")
            click.echo()
            
            karabiner.update_all_chords(all_chords)
            click.echo(f"✓ Refreshed {len(all_chords)} chords with dynamic sensitivity!")
            
            # Show a few examples
            if len(all_chords) > 0:
                click.echo("\n📋 Examples of updated chords:")
                for chord in all_chords[:3]:
                    sensitivity = karabiner.get_chord_sensitivity(chord)
                    click.echo(f"   • {'+'.join(chord.input_keys)} → {chord.output_text} ({sensitivity}ms)")
                if len(all_chords) > 3:
                    click.echo(f"   ... and {len(all_chords) - 3} more")
        else:
            click.echo("ℹ️  No chords found to refresh.")
            
    except Exception as e:
        click.echo(f"✗ Error refreshing chords: {str(e)}", err=True)
        ctx.exit(1)


@cli.command()
@click.option('--output-dir', type=click.Path(), help='Directory to export rule files to')
@click.option('--format', type=click.Choice(['integrated', 'modular']), default='integrated',
              help='Export format: integrated (single file) or modular (separate files)')
@click.pass_context
def export(ctx, output_dir, format):
    """Export chord rules to Karabiner configuration files."""
    chord_manager = ctx.obj['chord_manager']
    karabiner = ctx.obj['karabiner']
    
    try:
        all_chords = chord_manager.get_all_chords()
        if not all_chords:
            click.echo("ℹ️  No chords found to export.")
            return
        
        if format == 'modular':
            # Export to separate files
            click.echo("📁 Exporting chords to separate JSON files...")
            exported_files = karabiner.export_rules_to_files(all_chords, output_dir)
            
            click.echo(f"\n✓ Exported {len(all_chords)} chords to {len(exported_files)} files:")
            for filepath in exported_files:
                click.echo(f"   • {filepath.name}")
            
            click.echo(f"\n📍 Files saved to: {exported_files[0].parent}")
            click.echo("\n💡 To use these files with Karabiner:")
            click.echo("   1. Copy them to ~/.config/karabiner/assets/complex_modifications/")
            click.echo("   2. In Karabiner-Elements, go to Complex Modifications")
            click.echo("   3. Click 'Add rule' and select the FreeChorder rules")
        else:
            # Update integrated configuration
            click.echo("🔄 Updating integrated Karabiner configuration...")
            karabiner.update_all_chords(all_chords)
            click.echo(f"✓ Updated Karabiner with {len(all_chords)} chords")
            
    except Exception as e:
        click.echo(f"✗ Error exporting chords: {str(e)}", err=True)
        ctx.exit(1)


@cli.command()
@click.option('--enable', type=str, help='Enable a specific chord group')
@click.option('--disable', type=str, help='Disable a specific chord group')
@click.option('--list', 'list_groups', is_flag=True, help='List all chord groups and their status')
@click.pass_context
def groups(ctx, enable, disable, list_groups):
    """Manage chord groups (enable/disable groups of chords)."""
    chord_manager = ctx.obj['chord_manager']
    karabiner = ctx.obj['karabiner']
    
    all_chords = chord_manager.get_all_chords()
    
    if list_groups or (not enable and not disable):
        # Show group status
        click.echo("📋 Chord Groups:")
        click.echo("=" * 50)
        
        status = karabiner.get_group_status(all_chords)
        for group_name, info in sorted(status.items()):
            status_icon = "✓" if info['enabled'] else "✗"
            status_text = "enabled" if info['enabled'] else "disabled"
            click.echo(f"{status_icon} {group_name}: {info['chord_count']} chords ({status_text})")
            
            # Show a few example chords from each group
            if info['chord_count'] > 0:
                examples = info['chords'][:3]
                for chord in examples:
                    click.echo(f"   • {'+'.join(chord.input_keys)} → {chord.output_text}")
                if info['chord_count'] > 3:
                    click.echo(f"   ... and {info['chord_count'] - 3} more")
        
        click.echo("\n💡 Use --enable or --disable to toggle groups")
        return
    
    # Enable or disable a group
    if enable:
        enabled = karabiner.toggle_group(enable, enable=True)
        click.echo(f"✓ Enabled group: {enable}")
    elif disable:
        enabled = karabiner.toggle_group(disable, enable=False)
        click.echo(f"✗ Disabled group: {disable}")
    
    # Refresh Karabiner configuration
    click.echo("\n🔄 Updating Karabiner configuration...")
    karabiner.update_all_chords(all_chords)
    click.echo("✓ Configuration updated!")
    
    # Show current status
    click.echo("\n📊 Current group status:")
    status = karabiner.get_group_status(all_chords)
    enabled_count = sum(1 for info in status.values() if info['enabled'])
    click.echo(f"   • {enabled_count} groups enabled")
    click.echo(f"   • {len(status) - enabled_count} groups disabled")


@cli.command()
@click.argument('count', type=int, default=1)
@click.pass_context
def undo(ctx, count):
    """Undo the last N chord additions.
    
    COUNT: Number of chords to undo (default: 1)
    
    Examples:
      fc undo      # Undo last chord
      fc undo 3    # Undo last 3 chords
    """
    chord_manager = ctx.obj['chord_manager']
    karabiner = ctx.obj['karabiner']
    
    adder = InteractiveChordAdder(chord_manager, karabiner)
    adder.undo_last(count)


@cli.command()
@click.pass_context
def suggest(ctx):
    """Show suggested common chords to add.
    
    Displays a list of commonly used chords that you haven't added yet.
    """
    chord_manager = ctx.obj['chord_manager']
    karabiner = ctx.obj['karabiner']
    
    adder = InteractiveChordAdder(chord_manager, karabiner)
    adder.suggest_common_chords()


@cli.command()
@click.option('--skip-permission-check', is_flag=True, help='Skip accessibility permission check')
@click.pass_context
def impulse(ctx, skip_permission_check):
    """Enter impulse chording mode - create chords on-the-fly while typing."""
    chord_manager = ctx.obj['chord_manager']
    karabiner = ctx.obj['karabiner']
    
    # Check accessibility permissions
    if not skip_permission_check:
        click.echo("🔍 Checking accessibility permissions...")
        if not check_accessibility_permissions():
            click.echo("\n❌ Accessibility permissions not granted!")
            show_accessibility_instructions()
            
            if click.confirm("\n🔧 Would you like to open System Settings now?", default=True):
                open_accessibility_settings()
                click.echo("\n✅ After granting permissions:")
                click.echo("1. Restart your terminal")
                click.echo("2. Run 'freechorder impulse' again")
            else:
                click.echo("\n💡 To grant permissions manually, follow the instructions above.")
                click.echo("Then restart your terminal and try again.")
            
            ctx.exit(1)
        else:
            click.echo("✅ Accessibility permissions granted!\n")
    
    try:
        # Create and start impulse handler
        config = ctx.obj['config']
        handler = ImpulseHandler(chord_manager, karabiner, config)
        handler.start()
    except Exception as e:
        click.echo(f"\n✗ Error: {str(e)}", err=True)
        
        # Check if it's the specific accessibility error
        if "not trusted" in str(e) or "accessibility" in str(e).lower():
            click.echo("\n❌ Accessibility permissions issue detected!")
            show_accessibility_instructions()
            
            if click.confirm("\n🔧 Would you like to open System Settings?", default=True):
                open_accessibility_settings()
        else:
            click.echo("\nTroubleshooting:")
            click.echo("1. Grant accessibility permissions to your terminal")
            click.echo("2. Make sure Karabiner-Elements is running")
            click.echo("3. Restart your terminal after granting permissions")
        
        ctx.exit(1)


def main():
    """Main entry point."""
    return cli(standalone_mode=False)


if __name__ == '__main__':
    cli()
