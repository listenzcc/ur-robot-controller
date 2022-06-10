// Scripts after page loaded

console.log("After page loaded");

function onClick1(e) {
    console.log(e);
}

document.getElementById("mouse-panel-1").addEventListener("click", (event) => {
    console.log(event);

    const rx = event.offsetX / event.target.offsetWidth,
        ry = 1 - event.offsetY / event.target.offsetHeight;
    console.log(rx, ry);

    const x = parseInt(rx * 100),
        y = parseInt(ry * 100);

    const url = `upload/?x=${x}&y=${y}`;

    fetch(url);

    document.getElementById("mouse-panel-label-1").innerHTML = `x=${x}, y=${y}`;
});

console.log("After page loaded done");
