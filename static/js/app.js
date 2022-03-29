mutableElements = [document.querySelector('.app.chosen.option'), document.querySelector('.app.chosen.add'), document.querySelector('.app.chosen.transfer')]
localizedVars = { tracks: _('треки'), playlists: _('плейлисты'), artists: _('артисты'), albums: _("альбомы") }
chosenTracks = [];
chosenAlbums = [];
chosenArtists = [];
chosenPlaylists = [];

data = {
    "tracks": [],
    "artists": [],
    "albums": [],
    "playlists": [],
    "to_service": ''
}

currentOption = "{chosen}"

function appOnLoad() {
    changeDelta();
    replaceAllChosen(localizedVars.tracks);
    displayTracks();
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

function sendData(to_service) {

    data.to_service = to_service;
    console.log(data);
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
    if (currentOption != localizedVars.playlists) {
        deleteAllSongs();
        replaceAllChosen(localizedVars.playlists);
        displayData('playlists')
    }
    currentOption = localizedVars.playlists
}

function displayArtists() {
    if (currentOption != localizedVars.artists) {
        deleteAllSongs();
        replaceAllChosen(localizedVars.artists);
        displayData('artists')
    }
    currentOption = localizedVars.artists

}

function displayAlbums() {
    if (currentOption != localizedVars.albums) {
        deleteAllSongs();
        replaceAllChosen(localizedVars.albums);
        displayData('albums')
    }
    currentOption = localizedVars.albums

}

async function displayTracks() {
    if (currentOption != localizedVars.tracks) {
        deleteAllSongs();
        replaceAllChosen(localizedVars.tracks);
        displayData('tracks')
    }
    currentOption = localizedVars.tracks
}

async function displayData(data) {
    mainContainer = document.querySelector('.app.main-container')
    p_data = parseData()[`${data}`];
    setCount(p_data.length, "option")
    for (i in p_data) {
        add(p_data[i].id, p_data[i].title, p_data[i].service, p_data[i].album == undefined ? '' : p_data[i].album, p_data[i].artist == undefined ? '' : p_data[i].artist, mainContainer, data)
    }
    height = 162 + (p_data.length + 1) * (parseInt(window.getComputedStyle(document.querySelector('.app.song')).height.substring(0, window.getComputedStyle(document.querySelector('.app.song')).height.length - 2)) + 10);

    document.body.style.height = `calc(${height}px*var(--deltaH))`;
    mainContainer.style.height = `calc(${height}px*var(--deltaH))`;
}

function setCount(value, element) {
    if (value >= 0) {
        count = document.querySelector(`.app.chosen.${element}`).innerHTML
        _ = value
        document.querySelector(`.app.chosen.${element}`).innerHTML = count.substring(0, count.indexOf(':') + 2) + String(_)
    }

}

function getCount(element) {
    count = document.querySelector(`.app.chosen.${element}`).innerHTML
    _ = parseInt(count.substring(count.indexOf(':') + 1));
    return _;
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
    mainContainer = document.querySelector('.app.main-container')

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
    mainContainer.style.width = `calc(1050px*var(--deltaW))`

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
    mainContainer = document.querySelector('.app.main-container')

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
    mainContainer.style.width = `calc(1140px*var(--deltaW))`

    menuBtn.onclick = openMenu;
}

async function add(id, title, service, album, artist, mainContainer, type) {
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
        <input class="app song checkbox" onclick="choose(document.querySelector('.app.song.id${id}'), '${type}')" type="checkbox"></input>
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

function choose(object, type) {

    id = object.className.substring(object.className.indexOf("id") + 2)
    service = object.childNodes[5].className.substring(object.childNodes[5].className.indexOf("service") + 8);

    _ = { "id": id, "service": service }

    if (data[`${type}`].some(item => item.id === id)) {
        object.childNodes[1].checked = false;
        index = data[`${type}`].indexOf(_);
        data[`${type}`].splice(index, 1);
        setCount(getCount("count") - 1, "count")
        return;
    }
    object.childNodes[1].checked = true;




    data[`${type}`].push(_);

    setCount(getCount("count") + 1, "count")
}

function chooseAllSongs() {
    tracks = document.querySelectorAll('.app.song')
    for (let i = 8; i < tracks.length; i += 8) {
        choose(tracks[i])
    }
}

function deleteSong() {
    element = event.target.parentElement
    element.parentNode.removeChild(element)
    setCount(getCount("option") - 1, "option")
    setCount(getCount("count") - 1, "count")

}

function deleteAllSongs() {
    mainContainer = document.querySelector('.app.main-container')
    tracks = document.querySelectorAll('.app.song')
    for (let i = 8; i < tracks.length; i++) {
        tracks[i].parentNode.removeChild(tracks[i])
    }
    document.body.style.height = "100%";
    mainContainer.style.height = "max-content";
    setCount(0, "option")
    setCount(0, "count")

}

function showTransferPopUp() {
    document.querySelector('.app.popup').style.display = 'flex'
}

function chooseService(service) {
    document.querySelector('.app.popup').style.display = 'none'
    sendData(service)
}