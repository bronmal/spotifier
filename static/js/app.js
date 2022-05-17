const mutableElements = [document.querySelector('.app.chosen.option'), document.querySelector('.app.chosen.add'), document.querySelector('.app.chosen.transfer')]
const localizedVars = { tracks: _('треки'), playlists: _('плейлисты'), artists: _('артисты'), albums: _("альбомы") }
const socket = io();
const clusterize = new Clusterize({
    scrollId: 'scrollArea',
    contentId: 'contentArea',
    rows_in_block: 24
});

//TODO:
//Переделать дельты для разнвх типов обьектов например для картинок и остального
//Попробовать сделать анимацию на переход треков в Подключенных сервисах(необязательно)

class ObjectArray {
    constructor(dataType, lType) {
        this._dataType = dataType;
        this._localType = lType;
        this._value = []
        this._checkedObjects = new Map();
    }
    set value(value) {
        this._value = value;
    }
    get value() {
        return this._value;
    }
    get checkedObjects() {
        return this._checkedObjects;
    }
    getCheckedObjectsLength() {
        let j = 0;
        this._checkedObjects.forEach((v, k) => {
            if (v[0] === true) j += 1;
        })
        return j;
    }
    get checkedObjects() {
        return this._checkedObjects;
    }
    removeSong(songID) {
        let found = -1;
        this._value.forEach((v, i) => {
            if (v.id === songID) {
                this._value.splice(i, 1);
                found = 1;
            }
        })
        return found;
    }
    async push(value) {
        if (typeof value === 'object') {
            this._value.push(...value)
            this.addUncheckedObjects();
            if (currentOption === this._localType) {
                let songs = []
                for (let v of this._value) {
                    let song = await constructSong(v.id, v.title, v.service, v.album === undefined ? "" : v.album, v.artist === undefined ? '' : v.artist);
                    songs.push(song)
                }

                clusterize.update(songs)
                updateCountVars();
            }
            return;
        }
        this._value.push(value)
        this.addUncheckedObjects();
    }
    addUncheckedObjects() {
        this._value.forEach(e => {
            if (!this._checkedObjects.has(e.id))
                this._checkedObjects.set(e.id, [null, e.service]);
        });
    }
    async checkAllObjects() {
        this._checkedObjects.forEach((v, k) => {
            let songCheckbox = document.querySelector(`.app.song.id${k} > input`)
            let songService = this._checkedObjects.get(k)[1]
            if (songCheckbox)
                if (!songCheckbox.checked) songCheckbox.checked = true;
            this._checkedObjects.set(k, [true, songService]);
        })
        let songs = []
        for (let v of this._value) {
            let song = await constructSong(v.id, v.title, v.service, v.album === undefined ? "" : v.album, v.artist === undefined ? '' : v.artist);
            songs.push(song)
        }

        clusterize.update(songs)
        updateCountVars();
    }
    async uncheckAllObjects() {
        this._checkedObjects.forEach((v, k) => {
            let songCheckbox = document.querySelector(`.app.song.id${k} > input`)
            let songService = this._checkedObjects.get(k)[1]
            if (songCheckbox)
                if (!songCheckbox.checked) songCheckbox.checked = false;
            this._checkedObjects.set(k, [false, songService]);
        })
        let songs = []
        for (let v of this._value) {
            let song = await constructSong(v.id, v.title, v.service, v.album === undefined ? "" : v.album, v.artist === undefined ? '' : v.artist);
            songs.push(song)
        }

        clusterize.update(songs)
        updateCountVars();
    }
    checkObject(elementId) {
        let service = this._checkedObjects.get(elementId)[1]
        this._checkedObjects.set(elementId, [true, service]);
        updateCountVars();
    }
    uncheckObject(elementId) {
        let service = this._checkedObjects.get(elementId)[1]
        this._checkedObjects.set(elementId, [false, service]);
        updateCountVars();
    }

}
currentOption = "{chosen}"
notLocalizedCurrentOption = ''

let data = {
    _tracks: new ObjectArray("tracks", localizedVars.tracks),
    _artists: new ObjectArray("artists", localizedVars.artists),
    _albums: new ObjectArray("albums", localizedVars.albums),
    _playlists: new ObjectArray("playlists", localizedVars.playlists),
    _checkedObjectsLength: 0,
    _checkedObjects: [],
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
    get getCheckedObjectsLength() {
        return this._albums.getCheckedObjectsLength() + this._artists.getCheckedObjectsLength() + this._playlists.getCheckedObjectsLength() + this._tracks.getCheckedObjectsLength()
    },
    get checkedObjects() {
        return new Map([...this._albums.checkedObjects, ...this._artists.checkedObjects, ...this._playlists.checkedObjects, ...this._tracks.checkedObjects])
    }
}

function objectChecked(id) {
    if (data.checkedObjects.get(id)[0] === true) return true;
    else return false;
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
    document.querySelector('.app.song.top-part.checkbox').addEventListener('click', (e) => { chooseAllSongs(e.target) });
    document.querySelector('.app.song.top-part.delete').addEventListener('click', () => { deleteAllSongs() });
    document.querySelector('.app.popup-container.popup-service-container.service.spotify').addEventListener('click', (e) => { chooseService(e.target) })
    document.querySelector('.app.popup-container.popup-service-container.service.deezer').addEventListener('click', (e) => { chooseService(e.target) })
    document.querySelector('.app.popup-container.popup-service-container.service.vk').addEventListener('click', (e) => { chooseService(e.target) })
    document.querySelector('.app.popup-container.popup-service-container.service.yandex').addEventListener('click', (e) => { chooseService(e.target) })
    document.querySelector('.app.popup-container.goback-btn').addEventListener('click', () => { goBack() });
}

function appOnResize() {
    changeDelta();
}

async function goBack() {
    let progressBar = document.querySelector('.app.popup-container.progress-bar');
    let serviceContainer = document.querySelector('.app.popup-container.popup-service-container.non-selectable');
    let text = document.querySelector('.app.popup-container.popup-label.service-pick');
    let progressBarContainer = document.querySelector('.app.popup-container.progress-container');
    let text_ = document.querySelector('.app.popup-container.text');
    text_.classList.add('hidden');
    text_.innerHTML = '';
    progressBar.style.width = 0;
    progressBar.style.padding = 0;

    progressBarContainer.style.display = 'none';
    serviceContainer.parentElement.parentElement.style.display = 'none'
    serviceContainer.style.display = 'block';
    text.style.textAlign = 'left';
    text.style.marginLeft = 'calc(16px*var(--deltaW))';
    text.innerHTML = _('Выберите сервис для переноса:');

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
    let dataToSend = {
        "tracks": [],
        "artists": [],
        "albums": [],
        "playlists": [],
        "to_service": ''
    }

    let tracks = data.tracks.checkedObjects;
    tracks.forEach((v, k) => {
        if (v[0] === true) {
            dataToSend.tracks.push({ "id": k, "service": v[1] })
        }
    })
    let albums = data.albums.checkedObjects;
    albums.forEach((v, k) => {
        if (v[0] === true) {
            dataToSend.albums.push({ "id": k, "service": v[1] })
        }
    })
    let artists = data.artists.checkedObjects;
    artists.forEach((v, k) => {
        if (v[0] === true) {
            dataToSend.artists.push({ "id": k, "service": v[1] })
        }
    })
    let playlists = data.playlists.checkedObjects;
    playlists.forEach((v, k) => {
        if (v[0] === true) {
            dataToSend.playlists.push({ "id": k, "service": v[1] })
        }
    })


    return new Promise((resolve, reject) => {
        dataToSend.to_service = to_service;
        console.log(dataToSend);
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
    if (currentOption != type) {
        notLocalizedCurrentOption = valueT;
        deleteAllSongs();
        replaceAllChosen(type);
        document.querySelector('body > div.app.main-container > div.app.song.top-part > input').checked = false
    }
    if (currentOption === type) return;
    currentOption = type;
    data[notLocalizedCurrentOption].addUncheckedObjects();
    let songs = []
    for (let value of data[valueT].value) {
        songs.push(await constructSong(value.id, value.title, value.service, value.album === undefined ? "" : value.album, value.artist === undefined ? '' : value.artist))
    }
    clusterize.update(songs)

}

async function updateCountVars() {
    let tracks = document.querySelector('.app.chosen.option > strong')
    let selected = document.querySelector('.app.chosen.count > strong')
    tracks.innerHTML = data[notLocalizedCurrentOption].value.length
    selected.innerHTML = data.albums.getCheckedObjectsLength() + data.artists.getCheckedObjectsLength() + data.playlists.getCheckedObjectsLength() + data.tracks.getCheckedObjectsLength()

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

async function constructSong(id, title, service, album, artist) {
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
    if (objectChecked(id)) {
        song.innerHTML += `<input name="object" checked class="app song checkbox" type="checkbox" onclick="if (this.checked) data.tracks.checkObject('${id}'); else data.tracks.uncheckObject('${id}');"></input>`
    } else {
        song.innerHTML += `<input name="object" class="app song checkbox" type="checkbox" onclick="if (this.checked) data.tracks.checkObject('${id}'); else data.tracks.uncheckObject('${id}');"></input>`
    }

    song.innerHTML += `
        <label class="app song label">${title}</label>
        <img src="${servicePath}" class="app song service ${service}"></img>
        <div class="app song option1">${artist}</div>
        <div class="app song option2">${album}</div>
        <img src="/static/images/change-btn.svg" class="app song change-btn"></img>
        <img src="/static/images/delete-btn.svg" class="app song delete-btn" onclick="deleteSong(this)"></img>
        </input>`
    let someElement = song;
    let someElementToString;

    if (someElement.outerHTML)
        someElementToString = someElement.outerHTML;
    else if (XMLSerializer)
        someElementToString = new XMLSerializer().serializeToString(someElement);
    return someElementToString;


}

function getCheckedObjectsLength() {
    return data.tracks.getCheckedObjectsLength() + data.artists.getCheckedObjectsLength() + data.albums.getCheckedObjectsLength() + data.playlists.getCheckedObjectsLength();
}

async function chooseAllSongs(target) {
    if (!target.checked) data[notLocalizedCurrentOption].uncheckAllObjects();
    else data[notLocalizedCurrentOption].checkAllObjects();
}

async function deleteSong(element) {
    let songID = element.parentElement.classList[2].substring(2);
    console.log(songID);
    element.parentElement.parentElement.removeChild(element.parentElement)
    data[notLocalizedCurrentOption].removeSong(songID)
}

async function deleteAllSongs() {
    clusterize.update('');
    updateCountVars()
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
    sendData(service.classList[4])
    let count = 0;

    let dataToSend = {
        "tracks": [],
        "artists": [],
        "albums": [],
        "playlists": [],
        "to_service": ''
    }

    let tracks = data.tracks.checkedObjects;
    tracks.forEach((v, k) => {
        if (v[0] === true) {
            dataToSend.tracks.push({ "id": k, "service": v[1] })
        }
    })
    let albums = data.albums.checkedObjects;
    albums.forEach((v, k) => {
        if (v[0] === true) {
            dataToSend.albums.push({ "id": k, "service": v[1] })
        }
    })
    let artists = data.artists.checkedObjects;
    artists.forEach((v, k) => {
        if (v[0] === true) {
            dataToSend.artists.push({ "id": k, "service": v[1] })
        }
    })
    let playlists = data.playlists.checkedObjects;
    playlists.forEach((v, k) => {
        if (v[0] === true) {
            dataToSend.playlists.push({ "id": k, "service": v[1] })
        }
    })
    let text = document.querySelector('.app.popup-container.text')
    text.classList.remove('hidden');

    socket.on('audio_found', (msg, cb) => {
        let progressBar = document.querySelector('.app.popup-container.progress-bar');


        let sum = dataToSend.tracks.length + dataToSend.artists.length + dataToSend.albums.length + dataToSend.playlists.length;
        if (parseInt(msg.data) == 1) {
            count += parseInt(msg.data);
        } else {
            sum -= 1;
        }
        let d = (count / sum) * 100 + "%";


        // console.log('sum', sum);
        // console.log('d', d);
        // console.log('count', count);
        progressBar.style.width = d;
        progressBar.style.padding = '1%';

        text.innerHTML = msg.track;
        if (cb)
            cb();
    });
    let serviceContainer = document.querySelector('.app.popup-container.popup-service-container.non-selectable');
    let text_ = document.querySelector('.app.popup-container.popup-label.service-pick');
    let progressBarContainer = document.querySelector('.app.popup-container.progress-container');
    let serviceLogo = document.querySelector('.app.popup-container.image.serviceLogo');

    serviceLogo.src = `${service.src}`
    progressBarContainer.style.display = 'flex'
    serviceContainer.style.display = 'none';
    text_.style.textAlign = 'center';
    text_.style.marginLeft = 0;
    text_.innerHTML = _('Перенос треков');


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