function id_select(){
    document.getElementById('id_v2_selector').value = document.getElementById('id_selector').value
    if(document.getElementById('id_selector').value == 'None'){
        document.getElementById('dashboard_button').disabled = true
        document.getElementById('dashboard_v2_button').disabled = true
    }
    else{
        document.getElementById('dashboard_button').disabled = false
        document.getElementById('dashboard_v2_button').disabled = false
    }
}

function id_v2_select(){
    document.getElementById('id_selector').value = document.getElementById('id_v2_selector').value
    if(document.getElementById('id_v2_selector').value == 'None'){
        document.getElementById('dashboard_button').disabled = true
        document.getElementById('dashboard_v2_button').disabled = true
    }
    else{
        document.getElementById('dashboard_button').disabled = false
        document.getElementById('dashboard_v2_button').disabled = false
    }
} 
