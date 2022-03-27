mutableElements = [document.querySelector('.app.chosen.option'), document.querySelector('.app.chosen.add'), document.querySelector('.app.chosen.transfer')]
localizedVars = { tracks: _('треки'), playlists: _('плейлисты'), artists: _('артисты'), albums: _("альбомы") }
chosenTracks = [];
chosenAlbums = [];
chosenArtists = [];

currentOption = "{chosen}"

function appOnLoad() {
    replaceAllChosen(localizedVars.tracks);
    displayTracks();
    changeDelta();
}

function appOnResize() {
    changeDelta();
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
        displayData('artists')
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
        displayData('tracks')
    }
    currentOption = localizedVars.tracks
}

function displayData(data) {
    mainContainer = document.querySelector('.app.main-container')
    p_data = parseData()[`${data}`];
    count = document.querySelector('.app.chosen.option').innerHTML
    console.log(count);
    _ = parseInt(count.substring(count.indexOf(':') + 1));
    _ = p_data.length
    document.querySelector('.app.chosen.option').innerHTML = count.substring(0, count.indexOf(':') + 2) + String(_)
    for (i in p_data) {
        addSong(p_data[i].id, p_data[i].title, p_data[i].service, p_data[i].album == undefined ? '' : p_data[i].album, p_data[i].artist == undefined ? '' : p_data[i].artist, mainContainer)
    }
    height = 162 + (p_data.length + 1) * (parseInt(window.getComputedStyle(document.querySelector('.app.song')).height.substring(0, window.getComputedStyle(document.querySelector('.app.song')).height.length - 2)) + 10);

    document.body.style.height = `calc(${height}px*var(--deltaH))`;
    mainContainer.style.height = `calc(${height}px*var(--deltaW))`;
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
    slider = document.querySelector('.app.slider');
    personalInfo = document.querySelector('.app.personal-info');
    addedServices = document.querySelector('.app.added-services');
    musicContainer = document.querySelector('.app.music-container');
    transferMusicBtn = document.querySelector('.app.transfer-music');
    logo = document.querySelector('.app.spotifier-logo');
    menuBtn = document.querySelector('.app.menu-button');
    menuOptions = document.querySelector('.app.menu-options');

    intervalId = setInterval(() => {
        personalInfo.style.display = "block";
        addedServices.style.display = "block";
        musicContainer.style.display = "block";
        transferMusicBtn.style.display = "flex";
        logo.style.display = "block";
        clearInterval(intervalId);
    }, 200)


    menuBtn.style.height = `calc(24px*var(--deltaH))`;
    menuBtn.style.marginTop = `calc(16px*var(--deltaH))`;
    menuBtn.style.marginRight = `calc(16px*var(--deltaW))`;
    menuBtn.style.marginLeft = `calc(216px*var(--deltaW))`;
    menuBtn.style.marginBottom = "0px";

    menuBtn.src = "/static/images/menu-opened.svg";
    slider.style.width = `calc(256px*var(--deltaW))`;
    menuOptions.style.display = "none";

    menuBtn.onclick = hideMenu;

}

function hideMenu() {
    slider = document.querySelector('.app.slider');
    personalInfo = document.querySelector('.app.personal-info');
    addedServices = document.querySelector('.app.added-services');
    musicContainer = document.querySelector('.app.music-container');
    transferMusicBtn = document.querySelector('.app.transfer-music');
    logo = document.querySelector('.app.spotifier-logo');
    menuBtn = document.querySelector('.app.menu-button');
    menuOptions = document.querySelector('.app.menu-options');

    personalInfo.style.display = "none";
    addedServices.style.display = "none";
    musicContainer.style.display = "none";
    transferMusicBtn.style.display = "none";
    logo.style.display = "none";

    menuBtn.style.height = `calc(24px*var(--deltaH))`;
    menuBtn.style.marginTop = `calc(16px*var(--deltaH))`;
    menuBtn.style.marginRight = `calc(24px*var(--deltaW))`;
    menuBtn.style.marginLeft = `calc(24px*var(--deltaW))`;
    menuBtn.style.marginBottom = "0px";

    menuBtn.src = "/static/images/menu-closed.svg";
    slider.style.width = `calc(72px*var(--deltaW))`;
    menuOptions.style.display = "flex";

    menuBtn.onclick = openMenu;
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
    song.className = `app song id${id}`
    song.innerHTML = `
        <input class="app song checkbox" onclick="chooseSong()" type="checkbox"></input>
        <label class="app song label">${title}</label>
        <img src="${servicePath}" class="app song service ${service}"></img>
        <div class="app song option1">${artist}</div>
        <div class="app song option2">${album}</div>
        <img src="/static/images/change-btn.svg" class="app song change-btn" ></img>
        <img src="/static/images/delete-btn.svg" class="app song delete-btn" onclick="deleteSong()"></img>
        </input>`

    fragment.appendChild(song)
    mainContainer.appendChild(fragment)
}

function chooseSong() {
    song = event.target.parentNode
    if (chosenTracks.includes(song)) {
        index = chosenTracks.indexOf(song);
        chosenTracks.splice(index, 1);
        count = document.querySelector('.app.chosen.count').innerHTML
        _ = parseInt(count.substring(count.indexOf(':') + 1));
        _ -= 1;
        document.querySelector('.app.chosen.count').innerHTML = count.substring(0, count.indexOf(':') + 2) + String(_)
        return;
    }
    chosenTracks.push(song);
    count = document.querySelector('.app.chosen.count').innerHTML
    _ = parseInt(count.substring(count.indexOf(':') + 1));
    _ += 1;
    document.querySelector('.app.chosen.count').innerHTML = count.substring(0, count.indexOf(':') + 2) + String(_)

}

function deleteSong() {
    element = event.target.parentElement
    element.parentNode.removeChild(element)
}

function deleteAllSongs() {
    mainContainer = document.querySelector('.app.main-container')
    tracks = document.querySelectorAll('.app.song')
    for (let i = 8; i < tracks.length; i++) {
        tracks[i].parentNode.removeChild(tracks[i])
    }
    document.body.style.height = "100%";
    mainContainer.style.height = "max-content";
}

function changeSong() {

}