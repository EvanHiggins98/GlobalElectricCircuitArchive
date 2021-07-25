//v2_homepage id_selection
function id_select(){
    if(document.getElementById('id_selector').value == 'None'){
        document.getElementById('dashboard_button').disabled = true
    }
    else{
        document.getElementById('dashboard_button').disabled = false
    }
}  
