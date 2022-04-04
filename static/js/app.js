mutableElements = [document.querySelector('.app.chosen.option'), document.querySelector('.app.chosen.add'), document.querySelector('.app.chosen.transfer')]
localizedVars = { tracks: _('треки'), playlists: _('плейлисты'), artists: _('артисты'), albums: _("альбомы") }

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
    getServices();
    displayData('tracks', localizedVars.tracks);
}

function appOnResize() {
    changeDelta();
}

function getKeyByValue(object, value) {
    return Object.keys(object).find(key => object[key] === value);
}

async function parseData(url) {
    return new Promise(function(resolve, reject) {
        $(() => {
            $.ajax({
                url: url,
                type: 'GET',
                async: true,
                success: function(response) {
                    resolve(response)
                },
                error: function(response) {
                    return null;
                    reject(response)
                }
            })
        })
    })
}


async function parseServiceData(url, service, offset) {
    return new Promise(function(resolve, reject) {
        $(() => {
            $.ajax({
                url: url,
                type: 'GET',
                async: true,
                contentType: 'application/json;charset=UTF-8',
                dataType: 'json',
                data: { 'service': service, "offset": offset },
                success: function(response) {
                    resolve(response)
                },
                error: function(response) {
                    return null;
                    reject(response)
                }
            })
        })
    })
}

function sendData(to_service) {
    data.to_service = to_service;
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

async function displayData(data, type) {
    if (currentOption != type) {
        deleteAllSongs();
        replaceAllChosen(type);
    }
    length = 0
    currentOption = type

    parseData('http://127.0.0.1:5000/get_services').then((services) => {
        services = JSON.parse(services)
        len = 15
        offset = 0
        for (i = 0; i <= services.length; i++) {
            if (services[i] !== 'yandex' && services[i] !== 'deezer') {
                recursiveAddSongs(services[i], 0, data)

            } else {
                addSongs(services[i], data);
            }
        }
    })


}

async function addSongs(service, data) {
    parseServiceData('http://127.0.0.1:5000/get_audio', service, 0).then((response) => {
        console.log(response);
        mainContainer = document.querySelector('.app.main-container')
        p_data = response[data]
        offset += 15
        length += p_data.length

        for (i in p_data) {
            add(p_data[i].id, p_data[i].title, p_data[i].service, p_data[i].album == undefined ? '' : p_data[i].album, p_data[i].artist == undefined ? '' : p_data[i].artist, mainContainer, data)
        }
        setCount(length, "option")

        height = 162 + (length + 1) * (parseInt(window.getComputedStyle(document.querySelector('.app.song')).height.substring(0, window.getComputedStyle(document.querySelector('.app.song')).height.length - 2)) + 10);

        document.body.style.height = `calc(${height}px*var(--deltaH))`;
        mainContainer.style.height = `calc(${height}px*var(--deltaH))`;
    })
}

async function recursiveAddSongs(service, offset, data) {
    parseServiceData('http://127.0.0.1:5000/get_audio', service, offset).then((response) => {
        console.log(response);
        mainContainer = document.querySelector('.app.main-container')
        p_data = response[data]
        offset += 15
        len = p_data.length
        if (len === 15) {
            recursiveAddSongs(service, offset, data);
        }
        length += p_data.length

        for (i in p_data) {
            add(p_data[i].id, p_data[i].title, p_data[i].service, p_data[i].album == undefined ? '' : p_data[i].album, p_data[i].artist == undefined ? '' : p_data[i].artist, mainContainer, data)
        }
        setCount(length, "option")

        height = 162 + (length + 1) * (parseInt(window.getComputedStyle(document.querySelector('.app.song')).height.substring(0, window.getComputedStyle(document.querySelector('.app.song')).height.length - 2)) + 10);

        document.body.style.height = `calc(${height}px*var(--deltaH))`;
        mainContainer.style.height = `calc(${height}px*var(--deltaH))`;
    })
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
        case 'yandex':
            servicePath = '/static/images/yandex-logo.svg'
            break;
        case 'deezer':
            servicePath = '/static/images/deezer-logo.svg'
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
        <img src="/static/images/delete-btn.svg" class="app song delete-btn" onclick="deleteSong(this)"></img>
        </input>`

    fragment.appendChild(song)
    mainContainer.appendChild(fragment)
}

function choose(object, type) {
    id = object.className.substring(object.className.indexOf("id") + 2)
    service = object.childNodes[5].className.substring(object.childNodes[5].className.indexOf("service") + 8);

    _ = { "id": id, "service": service }

    if (data[`${type}`].some(item => (item.id === id && item.service === service))) {
        object.childNodes[1].checked = false;
        // index = data[`${type}`].indexOf(_);
        index = 0;
        for (key in data[`${type}`]) {
            value = data[`${type}`][key];
            if (id === value.id && service === value.service) {
                break;
            }
            index++;
        }
        data[`${type}`].splice(index, 1);
        setCount(getCount("count") - 1, "count")
        return;
    }
    object.childNodes[1].checked = true;
    data[`${type}`].push(_);
    setCount(getCount("count") + 1, "count")
}

function chooseAllSongs() {
    let tracks = document.querySelectorAll('.app.song')
    for (let i = 8; i < tracks.length; i += 8) {
        choose(tracks[i], getKeyByValue(localizedVars, chosenElement))
    }
}

function deleteSong(element) {
    element.parentElement.parentElement.removeChild(element.parentElement)
    setCount(getCount("option") - 1, "option")
    setCount(getCount("count") - 1, "count")
}

function deleteAllSongs() {
    mainContainer = document.querySelector('.app.main-container')
    tracks = document.querySelectorAll('.app.song')
    for (let i = 9; i < tracks.length; i += 8) {
        deleteSong(tracks[i])
    }
    document.body.style.height = "100%";
    mainContainer.style.height = "max-content";
}

function showTransferPopUp() {
    document.querySelector('.app.popup').style.display = 'flex'
}

function chooseService(service) {
    document.querySelector('.app.popup').style.display = 'none'
    sendData(service)
}

async function getServices() {
    parseData('http://127.0.0.1:5000/get_services').then((response) => {
        serviceElements = document.querySelectorAll('.app.added-services.service-container.service')
        for (i = 0; i < serviceElements.length; i++) {
            if (response.includes(serviceElements[i].className.substring(59, serviceElements[i].className.length))) {
                serviceElements[i].classList.remove('not-connected')
                serviceElements[i].removeAttribute('onclick')

            }
        }
    })
}

async function next() {
    let serviceBox = document.querySelector('.app.added-services.service-container.non-selectable');
    let servicesCount = serviceBox.childNodes.length;
    let firstService = serviceBox.childNodes[1];
    let lastService = serviceBox.childNodes[servicesCount - 2];
    serviceBox.removeChild(lastService);
    serviceBox.insertBefore(lastService, firstService);
}