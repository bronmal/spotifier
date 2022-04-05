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
    bindEvents();
    changeDelta();
    getServices();
    displayData('tracks', localizedVars.tracks);
}

async function bindEvents() {
    document.querySelector('.app.added-services.right-arrow-btn').addEventListener('click', () => { next('right') });
    document.querySelector('.app.added-services.left-arrow-btn').addEventListener('click', () => { next('left') });
    document.querySelector('.app.personal-info.logout').addEventListener('click', () => { logout() });
    document.querySelector('.app.menu-button').addEventListener('click', () => { openMenu() });
    document.querySelector('.app.transfer-music.non-selectable').addEventListener('click', () => { showTransferPopUp() });
    document.querySelector('.app.music-container.my-box.playlists').addEventListener('click', () => { displayData('playlists', localizedVars.playlists) });
    document.querySelector('.app.music-container.my-box.tracks').addEventListener('click', () => { displayData('tracks', localizedVars.playlists) });
    document.querySelector('.app.music-container.my-box.artists').addEventListener('click', () => { displayData('artists', localizedVars.playlists) });
    document.querySelector('.app.music-container.my-box.albums').addEventListener('click', () => { displayData('albums', localizedVars.playlists) });
    document.querySelector('.app.chosen.transfer.non-selectable').addEventListener('click', () => { showTransferPopUp() });
    document.querySelector('.app.song.top-part.checkbox').addEventListener('click', () => { chooseAllSongs() });
    document.querySelector('.app.song.top-part.delete').addEventListener('click', () => { deleteAllSongs() });
    document.querySelector('.app.popup-container.popup-service-container.service.spotify').addEventListener('click', () => { chooseService('spotify') })
    document.querySelector('.app.popup-container.popup-service-container.service.deezer').addEventListener('click', () => { chooseService('deezer') })
    document.querySelector('.app.popup-container.popup-service-container.service.vk').addEventListener('click', () => { chooseService('vk') })
    document.querySelector('.app.popup-container.popup-service-container.service.yandex').addEventListener('click', () => { chooseService('yandex') })
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

    parseData('http://127.0.0.1:5000/get_services').then((response) => {
        let services = JSON.parse(response)
        for (i = 0; i < services.length; i++) {
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
        let mainContainer = document.querySelector('.app.main-container')
        let p_data = response[data]
        length += p_data.length

        for (i in p_data) {
            add(p_data[i].id, p_data[i].title, p_data[i].service, p_data[i].album == undefined ? '' : p_data[i].album, p_data[i].artist == undefined ? '' : p_data[i].artist, mainContainer, data)
        }
        setCount(length, "option")

        let height = 162 + (length + 1) * (parseInt(window.getComputedStyle(document.querySelector('.app.song')).height.substring(0, window.getComputedStyle(document.querySelector('.app.song')).height.length - 2)) + 3);

        document.body.style.height = `calc(${height}px*var(--deltaH))`;
        mainContainer.style.height = `calc(${height}px*var(--deltaH))`;
    })
    return;
}

async function recursiveAddSongs(service, offset, data) {
    parseServiceData('http://127.0.0.1:5000/get_audio', service, offset).then((response) => {
        offset += 15
        let mainContainer = document.querySelector('.app.main-container')
        let p_data = response[data]
        let len = p_data.length
        if (len === 15) {
            recursiveAddSongs(service, offset, data);
        }
        length += p_data.length

        for (i in p_data) {
            add(p_data[i].id + offset, p_data[i].title, p_data[i].service, p_data[i].album == undefined ? '' : p_data[i].album, p_data[i].artist == undefined ? '' : p_data[i].artist, mainContainer, data)
        }
        setCount(length, "option")

        let height = 162 + (length + 1) * (parseInt(window.getComputedStyle(document.querySelector('.app.song')).height.substring(0, window.getComputedStyle(document.querySelector('.app.song')).height.length - 2)) + 3);

        document.body.style.height = `calc(${height}px*var(--deltaH))`;
        mainContainer.style.height = `calc(${height}px*var(--deltaH))`;
    })
}

function setCount(value, element) {
    if (value >= 0) {
        let count = document.querySelector(`.app.chosen.${element}`).innerHTML
        document.querySelector(`.app.chosen.${element}`).innerHTML = count.substring(0, count.indexOf(':') + 2) + String(value)
    }

}

function getCount(element) {
    let count = document.querySelector(`.app.chosen.${element}`).innerHTML
    let _ = parseInt(count.substring(count.indexOf(':') + 1));
    return _;
}

function replaceAllChosen(element) {
    chosenElement = element
    for (let i = 0; i < mutableElements.length; i++) {
        mutableElements[i].innerHTML = replaceChosen(mutableElements[i].innerHTML, chosenElement)
    }
}

function replaceChosen(string, replaceString) {
    let str = string.replace(currentOption, replaceString)
    return str
}

async function openMenu() {
    let slider = document.querySelector('.app.slider');
    let opened = slider.classList.contains('opened');
    let personalInfo = document.querySelector('.app.personal-info');
    let addedServices = document.querySelector('.app.added-services');
    let musicContainer = document.querySelector('.app.music-container');
    let transferMusicBtn = document.querySelector('.app.transfer-music');
    let logo = document.querySelector('.app.spotifier-logo');
    let menuBtn = document.querySelector('.app.menu-button');
    let menuOptions = document.querySelector('.app.menu-options');
    let mainContainer = document.querySelector('.app.main-container')
    if (opened) {
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
        slider.classList.replace('opened', 'clased');
    } else {
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
        slider.classList.replace('clased', 'opened');

    }
}

async function add(id, title, service, album, artist, mainContainer, type) {
    let fragment = new DocumentFragment();
    let song = document.createElement('div')
    let servicePath = ""
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
        <img src="/static/images/change-btn.svg" class="app song change-btn"></img>
        <img src="/static/images/delete-btn.svg" class="app song delete-btn"></img>
        </input>`

    fragment.appendChild(song)
    fragment.querySelector('.app.song.delete-btn').addEventListener('click', () => { deleteSong(document.querySelector('.app.song.delete-btn')) })
    mainContainer.appendChild(fragment)
}

function choose(object, type) {
    let id = object.className.substring(object.className.indexOf("id") + 2)
    let service = object.childNodes[5].className.substring(object.childNodes[5].className.indexOf("service") + 8);

    let _ = { "id": id, "service": service }

    if (data[`${type}`].some(item => (item.id === id && item.service === service))) {
        object.childNodes[1].checked = false;
        let index = 0;
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
    let mainContainer = document.querySelector('.app.main-container')
    let tracks = document.querySelectorAll('.app.song')
    for (let i = 9; i < tracks.length; i += 8) {
        deleteSong(tracks[i])
    }
    document.body.style.height = "100%";
    mainContainer.style.height = "max-content";
}

function showTransferPopUp() {
    document.querySelector('.app.popup').style.display = 'flex'
    parseData('/get_services').then((response) => {
        const services = JSON.parse(response);
        const visibleServices = document.querySelectorAll('.app.popup-container.popup-service-container.service');
        for (let i = 0; i < services.length; i++) {
            for (let j = 0; j < visibleServices.length; j++) {
                if ((visibleServices[j].classList.contains(services[i])) === true) {
                    visibleServices[j].style.display = "inline-block";
                }
            }
        }
    })
}

function chooseService(service) {
    document.querySelector('.app.popup').style.display = 'none'
    sendData(service)
}

async function getServices() {
    parseData('/get_services').then((response) => {
        let serviceElements = document.querySelectorAll('.app.added-services.service-container.service')
        for (i = 0; i < serviceElements.length; i++) {
            if (response.includes(serviceElements[i].className.substring(59, serviceElements[i].className.length))) {
                serviceElements[i].classList.remove('not-connected')
                serviceElements[i].removeAttribute('onclick')

            }
        }
    })
}

function next(direction) {
    if (direction === 'right') {
        let serviceBox = document.querySelector('.app.added-services.service-container.non-selectable');
        let firstService = serviceBox.firstElementChild;
        let lastService = serviceBox.lastElementChild;
        serviceBox.removeChild(lastService);
        serviceBox.insertBefore(lastService, firstService);
    } else {
        let serviceBox = document.querySelector('.app.added-services.service-container.non-selectable');
        let firstService = serviceBox.firstElementChild;
        serviceBox.removeChild(firstService);
        serviceBox.appendChild(firstService)
    }
}