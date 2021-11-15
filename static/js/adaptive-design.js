defaultWidth = 1920;
defaultHeight = 1080;
resizableObjects = {}



function resizeAllElements() {
    let resizableElements = document.querySelectorAll('.resizable');

    for (i = 0; i < resizableElements.length; i++) {
        if (resizableElements[i].offsetWidth !== document.body.offsetWidth & resizableElements[i].offsetHeight !== document.body.offsetHeight) {
            className = resizableElements[i].className;
            if (resizableObjects[className] === undefined) {
                style = window.getComputedStyle(resizableElements[i], null);
                styles = {}
                for (i in style) {
                    styles[i] = style[i]
                }
                resizableObjects[className] = styles;

            }

        }



    }
    for (i in resizableObjects) {
        deltaW = getResolution().Width / defaultWidth;
        deltaH = getResolution().Height / defaultHeight;

        originWidth = String(resizableObjects[i].width.substring(0, resizableObjects[i].width.length - 2));
        originHeight = String(resizableObjects[i].height.substring(0, resizableObjects[i].height.length - 2));

        originMarginLeft = String(resizableObjects[i].marginLeft.substring(0, resizableObjects[i].marginLeft.length - 2));
        originMarginRight = String(resizableObjects[i].marginRight.substring(0, resizableObjects[i].marginRight.length - 2));
        originMarginTop = String(resizableObjects[i].marginTop.substring(0, resizableObjects[i].marginTop.length - 2));
        originMarginBottom = String(resizableObjects[i].marginBottom.substring(0, resizableObjects[i].marginBottom.length - 2));

        originPaddingLeft = String(resizableObjects[i].paddingLeft.substring(0, resizableObjects[i].paddingLeft.length - 2));
        originPaddingRight = String(resizableObjects[i].paddingRight.substring(0, resizableObjects[i].paddingRight.length - 2));
        originPaddingTop = String(resizableObjects[i].paddingTop.substring(0, resizableObjects[i].paddingTop.length - 2));
        originPaddingBottom = String(resizableObjects[i].paddingBottom.substring(0, resizableObjects[i].paddingBottom.length - 2));


        needToBeResized = document.querySelectorAll(stringToHTMLClass(i))
        for (j = 0; j < needToBeResized.length; j++) {
            console.log();
            needToBeResized[j].style.width = (originWidth * deltaW) + "px";
            needToBeResized[j].style.height = (originHeight * deltaH) + "px";

            needToBeResized[j].style.marginTop = (originMarginTop * deltaH) + "px";
            needToBeResized[j].style.marginBottom = (originMarginBottom * deltaH) + "px";
            needToBeResized[j].style.marginRight = (originMarginRight * deltaW) + "px";
            needToBeResized[j].style.marginLeft = (originMarginLeft * deltaW) + "px";

            needToBeResized[j].style.paddingTop = (originPaddingTop * deltaH) + "px";
            needToBeResized[j].style.paddingBottom = (originPaddingBottom * deltaH) + "px";
            needToBeResized[j].style.paddingRight = (originPaddingRight * deltaW) + "px";
            needToBeResized[j].style.paddingLeft = (originPaddingLeft * deltaW) + "px";


        }

    }

}


function getResolution() {
    Resolution = {
        "Width": Math.max(document.documentElement.clientWidth),
        "Height": Math.max(document.documentElement.clientHeight)
    }

    return Resolution;
}

function stringToHTMLClass(text) {
    return '.' + text.split(' ').join('.');
}