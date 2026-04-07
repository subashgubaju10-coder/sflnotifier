$(function () {
    $('.inlinesparkline').sparkline(undefined,{
        type: 'line',
        width: '100px',
        lineColor: '#303F9F',
        fillColor: '#7986CB',
    })
    document.getElementById('btnSwitch').addEventListener('click',()=>{
        if (document.documentElement.getAttribute('data-bs-theme') == 'dark') {
            document.documentElement.setAttribute('data-bs-theme','light')
            $('#btnSwitch').html('<i class="bi bi-brightness-high"></i>')
            Cookies.set('theme', 'light', { expires: 36500 })
            localStorage.setItem('theme', 'light')
        }
        else {
            document.documentElement.setAttribute('data-bs-theme','dark')
            $('#btnSwitch').html('<i class="bi bi-moon"></i>')
            Cookies.set('theme', 'dark', { expires: 36500 })
            localStorage.setItem('theme', 'dark')
        }
    })
    window.onscroll = () => {
        toggleTopButton()
    }
})

function scrollToTop(){
    window.scrollTo({top: 0, behavior: 'smooth'})
}

function toggleTopButton() {
    if (document.body.scrollTop > 20 ||
        document.documentElement.scrollTop > 20) {
        document.getElementById('back-to-up').classList.remove('d-none')
    } else {
        document.getElementById('back-to-up').classList.add('d-none')
    }
}

function go(page='land') {
    if(!page || page==='undefined') page = 'land'
    console.log('go',page)
    var land_id = parseInt( $('#land_id').val() )
    if(land_id>0) window.location.href = '/'+page+'/'+land_id
}

function handle(e,page) {
    if (e.keyCode === 13) go(page)
}

async function update(land_id){
    console.log('land_id',land_id)
    try {
        $('#btnUpdate').hide()
        $('.btnUpdate').hide()
        $('#btnUpdateLoader').show()
        $('.btnUpdateLoader').show()
        const response = await fetch('https://sfl.world/update/' + land_id)
        let json = await response.json()
        console.log(json)
        console.log('wait4update',land_id)
        wait4update(land_id)
    } catch (error) {
        console.log(error)
    }
}
async function wait4update(land_id){
    try {
        const response = await fetch('https://sfl.world/update/'+land_id+'/check')
        let json = await response.json()
        console.log(json)
        if(json && json.status==='OK'){
            location.reload()
        }else{
            setTimeout(()=>{
                wait4update(land_id)
            },1000)
        }
    } catch (error) {
        console.log(error)
        setTimeout(()=>{
            wait4update(land_id)
        },1000)
    }
}
