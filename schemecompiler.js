const fs = require('fs');
const { Schematic } = require('mindustry-schematic-parser');

fs.readFile('scheme.msch', (err, base64) => {
    if (err) {
        console.error('Error reading scheme:', err);
        process.exit(1);
    }
    const buffer = Buffer.from(base64, 'base64')
    try {
        const schematic = Schematic.decode(buffer);

        const data = {
            name: schematic.name,
            description: schematic.description
        };
        console.log(JSON.stringify(data));
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