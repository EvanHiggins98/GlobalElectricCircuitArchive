function use_time_frame_clicked(cardName) {
    var checkbox = document.getElementById("use_time_frame_"+cardName);
    var timeFrame = document.getElementById("time_frame_"+cardName);
    timeFrame.hidden = !(checkbox.checked)
}