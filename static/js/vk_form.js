class Account {
    login = new String()
    password = new String()
    Account(login, password){
        this.login = login
        this.password = password
    }
}


function a(VkAccount, two_fa = null, code = null){
    session = new XMLHttpRequest()
    session.open('GET', "https://oauth.vk.com/token", false)
    session.setRequestHeader('Access-Control-Allow-Headers', 'Origin, X-Requested-With, Content-Type, Accept')
    session.setRequestHeader('Access-Control-Allow-Origin', '*')
    session.setRequestHeader('Access-Control-Allow-Method', 'GET')
    session.send({
        'grant_type': 'password',
        'client_id': '6146827',
        'client_secret': 'qVxWRF1CwHERuIrKBnqe',
        'username': VkAccount.login,
        'password': VkAccount.password,
        'v': '5.131',
        '2fa_supported': '1',
        'force_sms': two_fa !== null ? '1' : '0',
        'code': two_fa !== null ? code : '0'
    })
    session.onload = () => {console.log(session.status);}
}


function auth(){
    login = document.getElementById('login').value
    pass = document.getElementById('pass').value
    console.log(login);
    // $.post( "/test", {
    //     'login': VkAccount.login,
    //     'pass' : VkAccount.password 
    // })
    this.resp = null
    $(function () {
        $.ajax({
            url: '/test',
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
                    b()
                }
                console.log('dsfgdsfgdfsgdfgdsfgdfsgdfgdfgdfsgdfsgdsgdfsgdsgsdfgdfsgdfsg');
            },
            error: function (error) {}
        });
    })
    
    
}


function b() {
    console.log('asjdhnflkajshflkasdhfklasdhfkadshfjkasdhjf');
    document.getElementById('vk_auth_login').remove()
    document.getElementById('vk_auth_pass').remove()
    document.getElementById('hidden_2fa').style.display = 'block'
    value = document.getElementById('hidden_2fa')

}


function valid(VkAccount){
    response = auth(VkAccount)
    session = new Request()

    if ('validation_sid' in response) {
        session.get("https://api.vk.com/method/auth.validatePhone",
                    params={'sid': response['validation_sid'], 'v': '5.131'})
        code = input('Введите код из смс:  ')
        response = auth(vk_account, two_fa=True, code=code)
        print(response)

        if ('access_token' in response){
            return response['access_token'].json()
        }
    }
}