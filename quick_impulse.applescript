#!/usr/bin/osascript
-- Ultra-fast chord input dialog
-- No Python startup delay!

on run
    set promptResult to display dialog "Quick Chord Mode" & return & return & "Press 2+ keys, then click OK" default answer "" buttons {"Cancel", "OK"} default button "OK" with title "FreeChorder"
    
    if button returned of promptResult is "OK" then
        set chordKeys to text returned of promptResult
        
        if chordKeys is not "" then
            -- Get output text
            set outputResult to display dialog "Output for chord: " & chordKeys default answer "" buttons {"Cancel", "Save"} default button "Save" with title "FreeChorder"
            
            if button returned of outputResult is "Save" then
                set outputText to text returned of outputResult
                
                -- Save to quick cache
                set cacheFile to (POSIX path of (path to home folder)) & ".config/freechorder/.quick_chords_native"
                
                -- Append chord data
                set chordData to chordKeys & "|" & outputText & "|" & (do shell script "date +%s")
                do shell script "mkdir -p ~/.config/freechorder && echo " & quoted form of chordData & " >> " & cacheFile
                
                display notification "Chord saved! Run 'fc sync' to activate." with title "FreeChorder" subtitle (chordKeys & " → " & outputText)
            end if
        end if
    end if
end run
