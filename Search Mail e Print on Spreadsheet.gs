function searchMsg(){
  var thread = GmailApp.search("GMAIL SEARCH e.g. from:user@example.com");
  var recoveredFileId = "SPREADSHEET_ID";
  var recoveredFileSheet = "SHEET_NAME";
  var spreadsheet = SpreadsheetApp.openById(recoveredFileId);
  var sheet = spreadsheet.getSheetByName(recoveredFileSheet);
  var startDate = new Date("December 1, 2021 08:00:00").getTime(); //insert start date
  var endDate = new Date("January 31, 2022 17:00:00").getTime(); //insert end date
  var cc=0;
  for(var i in thread){
    var messages = thread[i].getMessages();
    for(var y=0; y<messages.length; y++){
      var msg = messages[y];
      var date = msg.getDate();
      var body = msg.getPlainBody();
      var bodyLength = body.length;
      if(date >= startDate && date <= endDate){
        var subject = msg.getSubject();
        var from = msg.getFrom();
        var to = msg.getTo();
        cc++;
        sheet.getRange(cc+2, 1).setValue(from);
        sheet.getRange(cc+2, 2).setValue(to);
        sheet.getRange(cc+2, 3).setValue(subject);
        sheet.getRange(cc+2, 4).setValue(date);
         if (bodyLength >= 50000){
          sheet.getRange(cc+2, 5).setValue('over 50000 characters')
         } else {        
        sheet.getRange(cc+2, 5).setValue(body)
        };
        Logger.log("DATE: " + date + "\nFROM: " + from + " SUBJECT: " + subject );
      }
    }
  }
}
