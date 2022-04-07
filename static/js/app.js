const mutableElements = [document.querySelector('.app.chosen.option'), document.querySelector('.app.chosen.add'), document.querySelector('.app.chosen.transfer')]
const localizedVars = { tracks: _('треки'), playlists: _('плейлисты'), artists: _('артисты'), albums: _("альбомы") }

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
    const songList = document.querySelector('.app.main-container')
    const config = { childList: true }
    const observer = new MutationObserver((mutationsList, observer) => {
        for (const mutation of mutationsList) {
            if (mutation.type === 'childList') {
                let count = document.querySelector(`.app.chosen.option`).innerHTML
                let length = songList.childElementCount - 5;
                document.querySelector(`.app.chosen.option`).innerHTML = count.substring(0, count.indexOf(':') + 2) + String(length)
                let height = 208 + length * 50;

                document.body.style.height = `calc(${height}px*var(--deltaH))`;
                songList.style.height = `calc(${height}px*var(--deltaH))`;
            }
        }
    })
    observer.observe(songList, config);



    document.querySelector('.app.added-services.right-arrow-btn').addEventListener('click', () => { next('right') });
    document.querySelector('.app.added-services.left-arrow-btn').addEventListener('click', () => { next('left') });
    document.querySelector('.app.personal-info.logout').addEventListener('click', () => { logout() });
    document.querySelector('.app.menu-button').addEventListener('click', () => { openMenu() });
    document.querySelector('.app.transfer-music.non-selectable').addEventListener('click', () => { showTransferPopUp() });
    document.querySelector('.app.music-container.my-box.playlists').addEventListener('click', () => { displayData('playlists', localizedVars.playlists) });
    document.querySelector('.app.music-container.my-box.tracks').addEventListener('click', () => { displayData('tracks', localizedVars.tracks) });
    document.querySelector('.app.music-container.my-box.artists').addEventListener('click', () => { displayData('artists', localizedVars.artists) });
    document.querySelector('.app.music-container.my-box.albums').addEventListener('click', () => { displayData('albums', localizedVars.albums) });
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

async function sendData(to_service) {
    return new Promise((resolve, reject) => {
        data.to_service = to_service;
        $(() => {
            $.ajax({
                url: '/send_audio',
                type: 'POST',
                contentType: 'application/json;charset=UTF-8',
                dataType: 'json',
                data: JSON.stringify(data),
                success: (response) => {
                    resolve(response)
                },
                error: (response) => {
                    reject(response)
                }
            })
        })
    })
}

async function displayData(data, type) {
    if (currentOption != type) {
        deleteAllSongs();
        replaceAllChosen(type);
    }
    if (currentOption === type) return;
    currentOption = type
    setCount(0, "option");
    let services = JSON.parse(await parseData('/get_services'))
    for (let service of services.sort()) {
        await recursiveGetSongs(service, 0, data, type)
    }
}

async function recursiveGetSongs(service, offset, data, type) {
    let mainContainer = document.querySelector('.app.main-container')

    let response = await parseServiceData('/get_audio', service, offset)
    if (currentOption !== type) {
        return null;
    }
    let ofs = offset + 15;
    let p_data = response[data]
    for (let song of p_data) {
        add(song.id, song.title, song.service, song.album == undefined ? '' : song.album, song.artist == undefined ? '' : song.artist, mainContainer, data)
    }
    let len = p_data.length
    if (len === 15) {
        let songs = await recursiveGetSongs(service, ofs, data, type);
        for (let song of songs) {
            p_data.push(song)
        }
    }
    console.log(p_data);
    return p_data;
}

async function setCount(value, element) {
    if (value >= 0) {
        let count = document.querySelector(`.app.chosen.${element}`).innerHTML
        document.querySelector(`.app.chosen.${element}`).innerHTML = count.substring(0, count.indexOf(':') + 2) + String(value)
    }
}

async function getCount(element) {
    let count = document.querySelector(`.app.chosen.${element}`).innerHTML
    let _ = parseInt(count.substring(count.indexOf(':') + 1));
    return _;
}

async function replaceAllChosen(element) {
    chosenElement = element
    for (let i = 0; i < mutableElements.length; i++) {
        replaceChosen(mutableElements[i].innerHTML, chosenElement).then((response) => { mutableElements[i].innerHTML = response })
    }
}

async function replaceChosen(string, replaceString) {
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

function add(id, title, service, album, artist, mainContainer, type) {
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
        <input class="app song checkbox" type="checkbox"></input>
        <label class="app song label">${title}</label>
        <img src="${servicePath}" class="app song service ${service}"></img>
        <div class="app song option1">${artist}</div>
        <div class="app song option2">${album}</div>
        <img src="/static/images/change-btn.svg" class="app song change-btn"></img>
        <img src="/static/images/delete-btn.svg" class="app song delete-btn"></img>
        </input>`
    fragment.appendChild(song)
    fragment.querySelector('.app.song.checkbox').addEventListener('click', () => { choose(document.querySelector(`.app.song.id${id}`), type) })
    fragment.querySelector('.app.song.delete-btn').addEventListener('click', () => { deleteSong(document.querySelector('.app.song.delete-btn')) })
    mainContainer.appendChild(fragment)
}

async function choose(object, type) {
    let id = object.className.substring(object.className.indexOf("id") + 2)
    let service = object.childNodes[5].className.substring(object.childNodes[5].className.indexOf("service") + 8);

    let _ = { "id": id, "service": service }

    if (data[type].some(item => (item.id === id && item.service === service))) {
        object.childNodes[1].checked = false;
        let index = 0;
        for (key in data[type]) {
            value = data[type][key];
            if (id === value.id && service === value.service) {
                break;
            }
            index++;
        }
        data[`${type}`].splice(index, 1);
        setCount(await getCount("count") - 1, "count")
        return;
    }
    object.childNodes[1].checked = true;
    data[`${type}`].push(_);
    setCount(await getCount("count") + 1, "count")
}

async function chooseAllSongs() {
    let tracks = document.querySelectorAll('.app.song')
    for (let i = 8; i < tracks.length; i += 8) {
        await choose(tracks[i], getKeyByValue(localizedVars, chosenElement))
    }
}

async function deleteSong(element) {
    element.parentElement.parentElement.removeChild(element.parentElement)
    setCount(await getCount("option") - 1, "option")
    setCount(await getCount("count") - 1, "count")
}

async function deleteAllSongs() {
    let mainContainer = document.querySelector('.app.main-container')
    let tracks = document.querySelectorAll('.app.song')
    for (let i = 9; i < tracks.length; i += 8) {
        deleteSong(tracks[i])
    }
    document.body.style.height = "100%";
    mainContainer.style.height = "max-content";
}

async function showTransferPopUp() {
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

async function chooseService(service) {
    document.querySelector('.app.popup').style.display = 'none'
    sendData(service)
}

async function getServices() {
    parseData('/get_services').then((response) => {
        const serviceElements = document.querySelectorAll('.app.added-services.service-container.service')
        const services = JSON.parse(response)
        for (const service of services) {
            for (const serviceElement of serviceElements) {
                if (serviceElement.classList.contains(service)) {
                    serviceElement.classList.remove('not-connected')
                }
            }
        }
    })
}

async function next(direction) {
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