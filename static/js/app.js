chosenElement = ""

function getTracks() {}

function choose() {
    options = [
        "personal-info",
        "add-service",
        "playlists",
        "tracks",
        "artists",
        "albums"
    ]
    element = event.target.className;
    for (i in options) {
        if (element.includes(options[i])) {
            element = options[i]
        }
    }
    chosenElement = element
    console.log(chosenElement);
    // switch (element) {
    //     case 'personal-info':
    //         chosenElement = element
    //         break;
    //     case 'add-service':
    //         chosenElement = element
    //         break;
    //     case 'playlists':
    //         chosenElement = element
    //         break;
    //     case 'tracks':
    //         chosenElement = element
    //         break;
    //     case 'artists':
    //         chosenElement = element
    //         break;
    //     case 'albums':
    //         chosenElement = element
    //         break;

    // }

}


function openMenu() {
    slider = document.querySelector('.resizable.app.slider');
    personalInfo = document.querySelector('.resizable.app.personal-info');
    addedServices = document.querySelector('.resizable.app.added-services');
    musicContainer = document.querySelector('.resizable.app.music-container');
    transferMusicBtn = document.querySelector('.resizable.app.transfer-music');
    logo = document.querySelector('.resizable.app.spotifier-logo');
    menuBtn = document.querySelector('.resizable.app.menu-button');
    menuOptions = document.querySelector('.resizable.app.menu-options');

    intervalId = setInterval(() => {
        personalInfo.style.display = "block";
        addedServices.style.display = "block";
        musicContainer.style.display = "block";
        transferMusicBtn.style.display = "flex";
        logo.style.display = "block";
        clearInterval(intervalId);
    }, 200)


    menuBtn.style.height = recomputeAttribute(24, deltaH) + "px";
    menuBtn.style.marginTop = recomputeAttribute(16, deltaH) + "px";
    menuBtn.style.marginRight = recomputeAttribute(16, deltaW) + "px";
    menuBtn.style.marginLeft = recomputeAttribute(216, deltaW) + "px";
    menuBtn.style.marginBottom = "0px";

    menuBtn.src = "/static/images/menu-opened.svg";
    slider.style.width = recomputeAttribute(256, deltaW) + "px";
    menuOptions.style.display = "none";

    menuBtn.onclick = hideMenu;

}

function hideMenu() {
    slider = document.querySelector('.resizable.app.slider');
    personalInfo = document.querySelector('.resizable.app.personal-info');
    addedServices = document.querySelector('.resizable.app.added-services');
    musicContainer = document.querySelector('.resizable.app.music-container');
    transferMusicBtn = document.querySelector('.resizable.app.transfer-music');
    logo = document.querySelector('.resizable.app.spotifier-logo');
    menuBtn = document.querySelector('.resizable.app.menu-button');
    menuOptions = document.querySelector('.resizable.app.menu-options');

    personalInfo.style.display = "none";
    addedServices.style.display = "none";
    musicContainer.style.display = "none";
    transferMusicBtn.style.display = "none";
    logo.style.display = "none";

    menuBtn.style.height = recomputeAttribute(24, deltaH) + "px";
    menuBtn.style.marginTop = recomputeAttribute(16, deltaH) + "px";
    menuBtn.style.marginRight = recomputeAttribute(24, deltaW) + "px";
    menuBtn.style.marginLeft = recomputeAttribute(24, deltaW) + "px";
    menuBtn.style.marginBottom = "0px";

    menuBtn.src = "/static/images/menu-closed.svg";
    slider.style.width = recomputeAttribute(72, deltaW) + "px";
    menuOptions.style.display = "flex";

    menuBtn.onclick = openMenu;
    updateStyles();
}



function displayTracks() {
    console.log(123);
}