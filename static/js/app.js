mutableElements = [document.querySelector('.resizable.app.chosen.option'), document.querySelector('.resizable.app.chosen.add'), document.querySelector('.resizable.app.chosen.transfer')]
localizedVars = { tracks: _('треки'), playlists: _('плейлисты'), artists: _('артисты'), albums: _("альбомы") }
chosenTracks = [];
chosenAlbums = [];
chosenArtists = [];

currentOption = "{chosen}"

//todo:
// отравлять в таком формате
// {
//     "tracks": [
//     {
//     "id": 123,
//     "service": "spotify"
//     },
//     {
//     "id": 122343,
//     "service": "vk"
//     }
//     ],
//     "albums": [
//     {
//     "id": 123,
//     "service": "spotify"
//     },
//     {
//     "id": 1345343,
//     "service": "vk"
//     }
//     ],
//     "artists": [
//     {
//     "id": 153,
//     "service": "spotify"
//     },
//     {
//     "id": 12266743,
//     "service": "vk"
//     }
//     ],
//     "playlists": [
//     {
//     "id": 12343,
//     "service": "spotify"
//     },
//     {
//     "id": 13463,
//     "service": "vk"
//     }
//     ],
//     "to_service": [
//     {
//     "to_service": "spotify"
//     }
//     ]
//     }

function appOnLoad() {
    replaceAllChosen("tracks");
    displayTracks();
    // resizeAllElements();
}

function appOnResize() {
    // resizeAllElements();
}

//ajax-query
function parseData() {
    var json = 0;
    $(() => {
        $.ajax({
            url: 'http://127.0.0.1:5000/get_audio',
            type: 'GET',
            async: false,
            success: function(response) {
                json = jQuery.parseJSON(response);
            }
        })
    })
    return json
}

function sendData() {

    data = {
        "tracks": [],
        "artists": [],
        "albums": [],
        "to_service": "vk"
    }
    for (let i = 0; i < chosenTracks.length; i++) {
        id = chosenTracks[i].className.substring(chosenTracks[i].className.indexOf("id") + 2)
        service = chosenTracks[i].childNodes[5].className.substring(chosenTracks[i].childNodes[5].className.indexOf("service") + 8);
        data.tracks.push({ "id": id, "service": service })
    }
    $(() => {
        $.ajax({
            url: 'http://127.0.0.1:5000/send_audio',
            type: 'POST',
            contentType: 'application/json;charset=UTF-8',
            dataType: 'json',
            data: JSON.stringify(data),
            success: (response) => {
                console.log(response);
            }
        })
    })
}


function displayPlaylists() {
    deleteAllSongs();
    currentOption = localizedVars.playlists
}

function displayArtists() {
    deleteAllSongs();
    if (currentOption != localizedVars.artists) {
        replaceAllChosen(localizedVars.artists);
        mainContainer = document.querySelector('.resizable.app.main-container')
        artists = parseData().artists;
        for (i in artists) {
            addSong(artists[i].id, artists[i].title, artists[i].service, artists[i].album, artists[i].artist, mainContainer)
        }
        height = 162 + (tracks.length + 1) * (window.getComputedStyle(document.querySelector('.app.resizable.song')).height + 10) + "px"
        document.body.style.height = height;
        mainContainer.style.height = height
    }
    currentOption = localizedVars.artists

}

function displayAlbums() {
    deleteAllSongs();
    currentOption = localizedVars.albums

}

function displayTracks() {
    deleteAllSongs();
    if (currentOption != localizedVars.tracks) {
        replaceAllChosen(localizedVars.tracks);
        mainContainer = document.querySelector('.resizable.app.main-container')
        tracks = parseData().tracks;
        for (i in tracks) {
            addSong(tracks[i].id, tracks[i].title, tracks[i].service, tracks[i].album, tracks[i].artist, mainContainer)
        }
        height = 162 + (tracks.length + 1) * (window.getComputedStyle(document.querySelector('.app.resizable.song')).height + 10) + "px";
        document.body.style.height = height;
        mainContainer.style.height = height;
    }
    currentOption = localizedVars.tracks
}

function replaceAllChosen(element) {
    chosenElement = element
    for (let i = 0; i < mutableElements.length; i++) {
        mutableElements[i].innerHTML = replaceChosen(mutableElements[i].innerHTML, chosenElement)
    }
}

function replaceChosen(string, replaceString) {
    str = string.replace(currentOption, replaceString)
    return str
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

async function addSong(id, title, service, album, artist, mainContainer) {
    let fragment = new DocumentFragment();
    var song = document.createElement('div')
    servicePath = ""
    switch (service) {
        case 'vk':
            servicePath = "/static/images/vk-logo1.svg";
            break;
        case 'spotify':
            servicePath = '/static/images/spotify-logo1.svg';
            break;
    }
    song.className = `resizable app song id${id}`
    song.innerHTML = `
        <input class="resizable app song checkbox" onclick="chooseSong()" type="checkbox"></input>
        <label class="resizable app song label">${title}</label>
        <img src="${servicePath}" class="resizable app song service ${service}"></img>
        <div class="resizable app song option1">${artist}</div>
        <div class="resizable app song option2">${album}</div>
        <img src="/static/images/change-btn.svg" class="resizable app song change-btn" ></img>
        <img src="/static/images/delete-btn.svg" class="resizable app song delete-btn" onclick="deleteSong()"></img>
        </input>`

    fragment.appendChild(song)
    mainContainer.appendChild(fragment)
}

function chooseSong() {
    song = event.target.parentNode
    if (chosenTracks.includes(song)) {
        index = chosenTracks.indexOf(song);
        chosenTracks.splice(index, 1)
        return;
    }
    chosenTracks.push(song);

    console.log(song);
}

function deleteSong() {
    element = event.target.parentElement
    element.parentNode.removeChild(element)
}

function deleteAllSongs() {
    mainContainer = document.querySelector('.resizable.app.main-container')
    tracks = document.querySelectorAll('.resizable.app.song')
    for (let i = 8; i < tracks.length; i++) {
        tracks[i].parentNode.removeChild(tracks[i])
    }
    document.body.style.height = "100%";
    mainContainer.style.height = "max-content";
}

function changeSong() {

}