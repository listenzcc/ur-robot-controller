// Scripts after page loaded

console.log("After page loaded");

{
    const canvas = document.getElementById("mouse-panel-canvas-1");
    const ctx = canvas.getContext("2d");
    const width = canvas.width;
    const height = canvas.height;

    const dst = { x: 50, y: 50 },
        src = { rx: 10, ry: 10, rz: 10 };

    function draw() {
        ctx.fillStyle = "#35333c";
        ctx.fillRect(0, 0, width, height);

        // Draw src
        {
            const { rx, ry, rz } = src;

            ctx.beginPath();
            ctx.strokeStyle = "#f0f000aa";
            ctx.arc(0, height, rz, 0, 2 * Math.PI, false);
            ctx.stroke();

            ctx.beginPath();
            ctx.strokeStyle = "#00f000aa";
            ctx.arc(0, 0, ry, 0, 2 * Math.PI, false);
            ctx.stroke();

            ctx.beginPath();
            ctx.strokeStyle = "#00f0f0aa";
            ctx.arc(width, height, rx, 0, 2 * Math.PI, false);
            ctx.stroke();
        }

        // Draw dst
        {
            const x = (dst.x / 100) * width,
                y = height - (dst.y / 100) * height,
                r = Math.min(width, height) / 40;
            ctx.strokeStyle = "#f0c9cf";
            ctx.lineWidth = r / 3;
            ctx.fillStyle = "#ee4863";
            ctx.fillRect(x, y, r, r);
            ctx.strokeRect(x, y, r, r);
        }
    }

    draw();

    function query() {
        const url = `query`;
        fetch(url).then((response) => {
            response.json().then((json) => {
                const { success, x, y, z, r } = json;
                console.log(success, x, y, z, r);

                src.rx = (x / r) * width;
                src.ry = (y / r) * width;
                src.rz = (z / r) * width;
                draw();
            });
        });
    }

    function keep_query() {
        const url = `query`;
        fetch(url).then((response) => {
            response.json().then((json) => {
                const { success, x, y, z, r } = json;
                console.log(success, x, y, z, r);

                src.rx = (x / r) * width;
                src.ry = (y / r) * width;
                src.rz = (z / r) * width;
                draw();
                keep_query();
            });
        });
    }

    keep_query();

    canvas.addEventListener("click", (event) => {
        console.log(event);

        // Read mouse click event
        const x = parseInt((event.offsetX / event.target.offsetWidth) * 100),
            y = parseInt((1 - event.offsetY / event.target.offsetHeight) * 100);
        console.log({ x, y });

        // Update the dst
        dst.x = x;
        dst.y = y;

        // Update the label
        document.getElementById(
            "mouse-panel-label-1"
        ).innerHTML = `x=${x}, y=${y}`;

        // Tell the backend
        {
            const url = `upload/?x=${x}&y=${y}`;
            fetch(url).then((response) => {
                response.json().then((json) => {
                    const { success, x, y } = json;
                    // console.log(success, x, y);
                });
            });
        }

        // Get the current position from the backend
        query();
    });
}

console.log("After page loaded done");
