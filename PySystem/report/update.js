var runFlag;
var url = location.href;
var url_path = url.substring(0, url.lastIndexOf('/')+1)

function updateStatus() {
  if (document.getElementById("running_status").getAttribute('status') == 'DONE') {
    return
  }
  var req = new XMLHttpRequest();
//  req.open('HEAD', location.href, false);
//  req.send(null);
//  var tc_update_file = 'tc_title'
  var update_file = 'tc_update'
  req.open('GET', url_path + update_file, false);
  req.setRequestHeader("Cache-Control", "max-age=0");
  req.send(null);
//  if (Date.parse(req.getResponseHeader('Last-Modified')) != Date.parse(document.lastModified)) {
  var curr_title = document.getElementById("curr_tc").getAttribute('title')
  var curr_status = document.getElementById("curr_tc").getAttribute('status')
//  if (req.responseText.trim() != tc_title) {
//    location.reload();
//    tc_title = req.responseText.trim()
//  }
  var tc_update = req.responseText;
  var split_loc = tc_update.indexOf(':');
  updated_title = tc_update.slice(0,split_loc).trim();
  updated_status = tc_update.slice(split_loc+1, tc_update.length).trim();
  if (updated_title != curr_title) {
    curr_title = updated_title;
    location.reload();
  } else if (updated_status != curr_status) {
    curr_status = updated_status;
    location.reload();
  }
  switch(runFlag) {
    case ">>>":
      runFlag = "###";
      break;
    case "###":
      runFlag = ">##";
      break;
    case ">##":
      runFlag = ">>#";
      break;
    case ">>#":
      runFlag = ">>>";
      break;
    default:
      runFlag = "###";
  }
  document.getElementById("curr_tc").innerHTML = runFlag + curr_title;
}
