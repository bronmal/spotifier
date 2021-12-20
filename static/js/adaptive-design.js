defaultWidth = 1440;
defaultHeight = 900;
resizableObjects = {}
Resolution = getResolution();
deltaW = Resolution.Width / defaultWidth;
deltaH = Resolution.Height / defaultHeight;

function recalcuteStyles() {
    let resizableElements = document.querySelectorAll('.resizable');
    for (i = 0; i < resizableElements.length; i++) {
        if (resizableElements[i].offsetWidth !== document.body.offsetWidth & resizableElements[i].offsetHeight !== document.body.offsetHeight) {
            className = resizableElements[i].className;
            if (className.baseVal !== undefined) {
                className = className.baseVal
            }
            if (resizableObjects[className] === undefined) {
                style = window.getComputedStyle(resizableElements[i], null);
                styles = {}
                for (k in style) {
                    styles[k] = style[k]
                }
                resizableObjects[className] = styles;
            }
        }
    }
}

function updateStyles() {
    let resizableElements = document.querySelectorAll('.resizable');
    for (i = 0; i < resizableElements.length; i++) {
        if (resizableElements[i].offsetWidth !== document.body.offsetWidth & resizableElements[i].offsetHeight !== document.body.offsetHeight) {
            className = resizableElements[i].className;
            if (resizableObjects[className] !== undefined) {
                style = window.getComputedStyle(resizableElements[i], null);
                styles = {}
                for (k in style) {
                    styles[k] = style[k]
                }
                resizableObjects[className] = styles;
            }
        }
    }
}

function recomputeStyle(element) {
    className = element.className;
    if (resizableObjects[className] !== undefined) {
        style = window.getComputedStyle(element, null);
        styles = {}
        for (k in style) {
            styles[k] = style[k]
        }
        resizableObjects[className] = styles;
    }
    console.log(element);
}


function resizeAllElements() {
    recalcuteStyles();
    for (i in resizableObjects) {

        originWidth = getAttribute("width", resizableObjects[i]);
        originHeight = getAttribute("height", resizableObjects[i]);

        originMarginLeft = getAttribute("marginLeft", resizableObjects[i]);
        originMarginRight = getAttribute("marginRight", resizableObjects[i]);
        originMarginTop = getAttribute("marginTop", resizableObjects[i]);
        originMarginBottom = getAttribute("marginBottom", resizableObjects[i]);

        originPaddingLeft = getAttribute("paddingLeft", resizableObjects[i]);
        originPaddingRight = getAttribute("paddingRight", resizableObjects[i]);
        originPaddingTop = getAttribute("paddingTop", resizableObjects[i]);
        originPaddingBottom = getAttribute("paddingBottom", resizableObjects[i]);

        originFontSize = getAttribute("fontSize", resizableObjects[i]);


        needToBeResized = document.querySelectorAll(stringToHTMLClass(i))
        for (j = 0; j < needToBeResized.length; j++) {
            needToBeResized[j].style.width = recomputeAttribute(originWidth, deltaW) + "px";
            needToBeResized[j].style.height = recomputeAttribute(originHeight, deltaH) + "px";

            needToBeResized[j].style.marginTop = recomputeAttribute(originMarginTop, deltaH) + "px";
            needToBeResized[j].style.marginBottom = recomputeAttribute(originMarginBottom, deltaH) + "px";
            needToBeResized[j].style.marginRight = recomputeAttribute(originMarginRight, deltaW) + "px";
            needToBeResized[j].style.marginLeft = recomputeAttribute(originMarginLeft, deltaW) + "px";

            needToBeResized[j].style.paddingTop = recomputeAttribute(originPaddingTop, deltaH) + "px";
            needToBeResized[j].style.paddingBottom = recomputeAttribute(originPaddingBottom, deltaH) + "px";
            needToBeResized[j].style.paddingRight = recomputeAttribute(originPaddingRight, deltaW) + "px";
            needToBeResized[j].style.paddingLeft = recomputeAttribute(originPaddingLeft, deltaW) + "px";

            needToBeResized[j].style.fontSize = recomputeAttribute(originFontSize, deltaW) + "px";

        }

    }

}

function getAttribute(p_attribute, p_element) {
    attribute = String(p_element[p_attribute].substring(0, p_element[p_attribute].length - 2));
    return attribute;
}

function recomputeAttribute(attribute, delta) {
    return attribute < delta * defaultHeight ? attribute * delta : attribute;
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