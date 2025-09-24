#!/bin/bash
echo "Pokretanje Token Creator Widget..."
echo ""
echo "Otvaram index.html u default browseru..."

# Try different commands for different systems
if command -v xdg-open &> /dev/null; then
    xdg-open index.html
elif command -v open &> /dev/null; then
    open index.html
elif command -v sensible-browser &> /dev/null; then
    sensible-browser index.html
else
    echo "Nije moguće automatski otvoriti browser."
    echo "Molimo otvorite index.html ručno."
fi

echo ""
echo "Widget je otvoren! Ako se ne otvori automatski, otvorite index.html ručno."
echo ""
read -p "Pritisnite Enter za zatvaranje..."

