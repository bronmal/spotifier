var a = '<div id="removable"><div>АВТОРИЗАЦИЯ VK</div><input type="login" id="log"> <input type="password" id="pass"></div>';
var b = document.getElementById("hidden");
var button = document.getElementById("btn");
b.style.display = "none";
function test() {
    if (document.getElementById("hidden").style.display == "none") {
        b.insertAdjacentHTML("afterbegin", a);
        document.getElementById("hidden").style.display = "inline-block";
        return;
    }
    var validLog = "admin";
    var validPass = "admin";
    if (document.getElementById("log") && document.getElementById("pass")) {
        if (document.getElementById("log").value === validLog &&
            document.getElementById("pass").value === validPass) {
            console.log("123123123123121312sex");
            a = '<div id="removable"><button style="background-color:green">АВТОРИЗАЦИЯ В SPOTIFY</button></div>';
        }
    }
    var c = document.getElementById("removable");
    c.parentNode.removeChild(c);
    document.getElementById("hidden").style.display = "none";
}

function redirect() {
    location.replace('/auth_vk')
}
