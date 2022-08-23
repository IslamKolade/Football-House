const check = document.getElementById('passcheck1')
const check2 = document.getElementById('passcheck2')
function clicked1() {
    if (check.type === 'password'){
        check.type = 'text';
    }
    else{
        check.type = 'password';
    }
}

function clicked2() {
    if (check2.type === 'password'){
        check2.type = 'text';
    }
    else{
        check2.type = 'password';
    }
}