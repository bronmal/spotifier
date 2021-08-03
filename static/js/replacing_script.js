let success = false
let intervalId;
let intervalId2;
let elem;

async function a() {
    let m = document.getElementById("transfer"),
        i = 0;
    elem = document.querySelector(".btn-start button")
    elem.classList.add("no-transition")
    let triggerLayout = elem.offsetHeight;
    intervalId = setInterval(function () {
        m.innerHTML = m.innerHTML + '.'
        
        i++;
        if(i === 4){
            i = 0
            m.innerHTML = 'перенос'

        }
    }, 500);
}

async function d(){
    let a = document.getElementById("hidden")
    intervalId2 = setInterval(() => {
        a.style.fontWeight = 'normal'
        a.innerHTML = "Похоже у вас много треков вконтакте, не беспокойтесь мы все ещё переносим их"
        clearInterval(intervalId2)
    }, 30000)  
    a.style.fontWeight = 'bold' 
}

async function b(){
    $(function () {
        $.ajax({
            url: '/transfer',
            type: 'GET',
            success: function (response) {
                elem.classList.remove("no-transition")
                document.getElementById("transfer").innerHTML = "завершено"
                const json = jQuery.parseJSON(response);
                if (isNaN(json.errors)) {
                    for (let key in json.errors) {
                        $("#errors_transfer").append("<option>" + json.errors[key] + "</option>")
                    }
                    $("#errors").css("display", "block");
                }

                clearInterval(intervalId)
                clearInterval(intervalId2)
                c()
            },
            error: function (error) {}
        });
    })
}

async function c() {
    $(function () {
        $.ajax({
            url: '/pay',
            type: 'GET',
            success: function (response) {
                const json = jQuery.parseJSON(response);
                if (json.url_to_pay !== null)
                {
                    document.getElementById("transfer").setAttribute("onclick", 'window.location.href = ' + "'" + json.url_to_pay + "'")
                    document.getElementById("transfer").innerHTML = "Оплатить 69 руб*"
                    document.getElementById("user_agreement").style.display = "block"
                    document.getElementById("hidden").innerHTML = "Вы перенесли 100 треков, чтобы переносить без ограничений заплатите 69 рублей"
                    document.getElementsByClassName("btn-start")[0].style.marginTop = 10 + "px";
                }
            },
            error: function (error) {
                console.log(error);
            }
        });
    })
}
a()
d()
b()