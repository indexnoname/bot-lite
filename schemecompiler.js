const fs = require('fs');
const { Schematic } = require('mindustry-schematic-parser');

fs.readFile('scheme.msch', 'utf8', (err, base64) => {
    if (err) {
        console.error('Error reading scheme:', err);
        process.exit(1);
    }
    console.log(Buffer.from(base64, 'base64'))
    try {
        const schematic = Schematic.decode(Buffer.from(base64, 'base64'));

        // Save schematic info to a JSON file
        const schematicInfo = {
            name: schematic.name,
            description: schematic.description,
        };
        fs.writeFileSync('/home/nonamecoding/Desktop/bots/json/scheme_info.json', JSON.stringify(schematicInfo, null, 2));

        schematic
            .render({
                background: true // enable background
            })
            .then(nodeCanvas => nodeCanvas.toBuffer())
            .then(buffer => fs.writeFileSync('scheme.png', buffer))
            .then(() => process.exit(0))
            .catch(err => {
                console.error('Error rendering scheme:', err);
                process.exit(1);
            });
    } catch (err) {
        console.error('Error decoding scheme:', err);
        process.exit(1);
    }
});