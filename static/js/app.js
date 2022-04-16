const mutableElements = [document.querySelector('.app.chosen.option'), document.querySelector('.app.chosen.add'), document.querySelector('.app.chosen.transfer')]
const localizedVars = { tracks: _('треки'), playlists: _('плейлисты'), artists: _('артисты'), albums: _("альбомы") }

//TODO:
//Пересмотреть формулы высоты маинконтейнер
//Переделать дельты для разнвх типов обьектов например для картинок и остального
//Выбрать нормальный крестик
//Добавить анимацию при переносе
//Попробовать сделать анимацию на переход треков в Подключенных сервисах(необязательно)

class ObjectArray {
    constructor(dataType, lType) {
        this._dataType = dataType;
        this._localType = lType;
        this._value = []
    }
    set value(value) {
        this._value = value;
    }
    get value() {
        return this._value;
    }
    push(value) {
        if (typeof value === 'object') {
            this._value.push(...value)
            if (currentOption === this._localType) {
                let mainContainer = document.querySelector('.app.main-container')
                for (let v of value) {
                    add(v.id, v.title, v.service, v.album === undefined ? "" : v.album, v.artist === undefined ? '' : v.artist)
                    updateCountVars();
                    mainContainer.style.height = this._value.length * 50 + 208 * deltaH + "px"
                    document.body.style.height = this._value.length * 50 + 208 * deltaH + "px"
                }
            }
            return;
        }
        this._value.push(value)
    }
}
currentOption = "{chosen}"

let data = {
    _tracks: new ObjectArray("tracks", localizedVars.tracks),
    _artists: new ObjectArray("artists", localizedVars.artists),
    _albums: new ObjectArray("albums", localizedVars.albums),
    _playlists: new ObjectArray("playlists", localizedVars.playlists),
    set tracks(value) {
        this._tracks = value;
    },
    get tracks() {
        return this._tracks;
    },
    set artists(value) {
        this._artists = value;
    },
    get artists() {
        return this._artists;
    },
    set albums(value) {
        this._albums = value;
    },
    get albums() {
        return this._albums;
    },
    set playlists(value) {
        this._playlists = value;
    },
    get playlists() {
        return this._playlists;
    },
}




function appOnLoad() {
    parseData('/get_services').then(async(response) => {
        displayData('tracks', localizedVars.tracks);
        for (let service of JSON.parse(response).sort()) {
            await recursiveGetSongs(service, 0, "tracks")
        }

    })
    bindEvents();
    changeDelta();
    getServices();
}

async function bindEvents() {
    document.querySelector('.app.added-services.right-arrow-btn').addEventListener('click', () => { next('right') });
    document.querySelector('.app.added-services.left-arrow-btn').addEventListener('click', () => { next('left') });
    document.querySelector('.app.personal-info.logout').addEventListener('click', () => { window.location.replace("/logout") });
    document.querySelector('.app.menu-button').addEventListener('click', () => { openMenu() });
    document.querySelector('.app.transfer-music.non-selectable').addEventListener('click', () => { showTransferPopUp() });
    document.querySelector('.app.music-container.my-box.playlists').addEventListener('click', async() => {
        await displayData('playlists', localizedVars.playlists);
        updateCountVars();
    });
    document.querySelector('.app.music-container.my-box.tracks').addEventListener('click', async() => {
        await displayData('tracks', localizedVars.tracks);
        updateCountVars()
    });
    document.querySelector('.app.music-container.my-box.artists').addEventListener('click', async() => {
        await displayData('artists', localizedVars.artists);
        updateCountVars()
    });
    document.querySelector('.app.music-container.my-box.albums').addEventListener('click', async() => {
        await displayData('albums', localizedVars.albums);
        updateCountVars()
    });
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
                }
            })
        })
    })
}

async function sendData(to_service) {
    let checked = getCheckedObjects();
    let dataToSend = {
        "tracks": [],
        "artists": [],
        "albums": [],
        "playlists": [],
        "to_service": ''
    }

    for (let object of checked) {
        let id = object.parentNode.classList[2].substring(2)
        let service = object.parentNode.childNodes[5].className.substring(object.parentNode.childNodes[5].className.indexOf("service") + 8);
        for (let i of data.tracks.value) {
            if (i.id === id) {
                dataToSend.tracks.push({ "id": id, "service": service })
            }
        }
        for (let i of data.artists.value) {
            if (i.id === id) {
                dataToSend.artists.push({ "id": id, "service": service })
            }
        }
        for (let i of data.albums.value) {
            if (i.id === id) {
                dataToSend.albums.push({ "id": id, "service": service })
            }
        }
        for (let i of data.playlists.value) {
            if (i.id === id) {
                dataToSend.playlists.push({ "id": id, "service": service })
            }
        }
    }


    return new Promise((resolve, reject) => {
        dataToSend.to_service = to_service;
        $(() => {
            $.ajax({
                url: '/send_audio',
                type: 'POST',
                contentType: 'application/json;charset=UTF-8',
                dataType: 'json',
                data: JSON.stringify(dataToSend),
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

async function displayData(valueT, type) {
    let mainContainer = document.querySelector('.app.main-container')
    if (currentOption != type) {
        deleteAllSongs();
        replaceAllChosen(type);
        document.querySelector('body > div.app.main-container > div.app.song.top-part > input').checked = false
    }
    if (currentOption === type) return;
    currentOption = type
    for (let value of data[valueT].value) {
        add(value.id, value.title, value.service, value.album === undefined ? "" : value.album, value.artist === undefined ? '' : value.artist)
    }
    mainContainer.style.height = data[valueT].value.length * 50 * deltaH + 208 * deltaH + "px"
    document.body.style.height = data[valueT].value.length * 50 * deltaH + 208 * deltaH + "px"


}

async function updateCountVars() {
    let tracks = document.querySelector('.app.chosen.option')
    let selected = document.querySelector('.app.chosen.count')
    let songs = document.querySelectorAll('.app.song')
    let count = 0
    for (let song of songs) {
        if (song.className.includes('id')) {
            count++;
            document.querySelector('.app.chosen.option').innerHTML = tracks.innerHTML.substring(0, tracks.innerHTML.indexOf(':') + 2) + String(count)
            document.querySelector('.app.chosen.count').innerHTML = selected.innerHTML.substring(0, selected.innerHTML.indexOf(':') + 2) + String(getCheckedObjects().length)
        }
        if (song.classList.contains('hidden')) {
            count--;
            document.querySelector('.app.chosen.option').innerHTML = tracks.innerHTML.substring(0, tracks.innerHTML.indexOf(':') + 2) + String(count)
            document.querySelector('.app.chosen.count').innerHTML = selected.innerHTML.substring(0, selected.innerHTML.indexOf(':') + 2) + String(getCheckedObjects().length)
        }
    }
}

async function recursiveGetSongs(service, offset, valueT) {
    let response = await parseServiceData('/get_audio', service, offset)
    let ofs = offset + 15;
    let keys = [...Object.keys(response)]

    for (let key of keys) {
        data[key].push([...response[key]])
    }
    if (response[valueT].length === 15) {
        await recursiveGetSongs(service, ofs, valueT);

    }

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

async function add(id, title, service, album, artist) {
    let mainContainer = document.querySelector('.app.main-container')
    let songs = document.querySelectorAll('.app.song')


    for (let song of songs) {
        if (song.classList.contains(`id${id}`)) {
            song.classList.remove('hidden')

            return;
        }
    }
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
        <input name="object" class="app song checkbox" type="checkbox"></input>
        <label class="app song label">${title}</label>
        <img src="${servicePath}" class="app song service ${service}"></img>
        <div class="app song option1">${artist}</div>
        <div class="app song option2">${album}</div>
        <img src="/static/images/change-btn.svg" class="app song change-btn"></img>
        <img src="/static/images/delete-btn.svg" class="app song delete-btn"></img>
        </input>`
    fragment.appendChild(song)
    fragment.querySelector('.app.song.checkbox').addEventListener('click', () => { updateCountVars() })
    fragment.querySelector('.app.song.delete-btn').addEventListener('click', () => { deleteSong(document.querySelector('.app.song.delete-btn')) })
    mainContainer.appendChild(fragment)



}

function getCheckedObjects() {
    return document.querySelectorAll('input[name=object]:checked');
}

async function chooseAllSongs() {
    let tracks = document.querySelectorAll('.app.song')
    let checked = document.querySelector('body > div.app.main-container > div.app.song.top-part > input').checked
    for (let i = 9; i < tracks.length; i += 8) {
        if (!tracks[i].parentElement.classList.contains('hidden')) {
            tracks[i].checked = checked
        }
    }
    updateCountVars();
}

async function deleteSong(element) {
    element.parentElement.classList.add('hidden')
}

async function deleteAllSongs() {
    let tracks = document.querySelectorAll('.app.song')
    updateCountVars()
    for (let i = 9; i < tracks.length; i += 8) {
        deleteSong(tracks[i])
    }
    document.body.style.height = "100%";
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