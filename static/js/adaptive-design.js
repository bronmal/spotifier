defaultWidth = 1440;
defaultHeight = 900;
deltaW = 1;
deltaH = 1;

function changeDelta() {
    updateDelta();
    let r = document.querySelector(":root");
    r.style.setProperty('--deltaH', deltaH);
    r.style.setProperty('--deltaW', deltaW);
}

function updateDelta() {
    mid = (getResolution().Width / defaultWidth + getResolution().Height / defaultHeight) / 2;
    deltaW = getResolution().Width / defaultWidth;
    deltaH = (getResolution().Height + 105) / defaultHeight;
}

function getResolution() {
    Resolution = {
        "Width": Math.max(window.innerWidth),
        "Height": Math.max(window.innerHeight)
    }

    return Resolution;
}

function stringToHTMLClass(text) {
    return '.' + text.split(' ').join('.');
}