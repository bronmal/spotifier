defaultWidth = 1440;
defaultHeight = 900;
deltaW = 1;
deltaH = 1;
root = document.querySelector(":root");

function changeDelta() {
    updateDelta();
    if (getResolution().Height > 600 && getResolution().Width > 1000) {
        document.body.style.width = `none`
        root.style.setProperty('--deltaH', deltaH);
        root.style.setProperty('--deltaW', deltaW);
    } else {
        deltaH = 1;
        deltaW = 1;
        document.body.style.width = `calc(1440px*var(--deltaW))`
    }

}

function updateDelta() {
    mid = (getResolution().Width / defaultWidth + getResolution().Height / defaultHeight) / 2;
    deltaW = getResolution().Width / defaultWidth;
    deltaH = (getResolution().Height + 105) / defaultHeight;
}

function getResolution() {
    Resolution = {
        "Width": $(window).width(),
        "Height": $(window).height()
    }

    return Resolution;
}

function stringToHTMLClass(text) {
    return '.' + text.split(' ').join('.');
}