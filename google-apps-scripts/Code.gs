function customOnEdit(e) {
  if (!e || !e.range) {
    Logger.log("❌ Error: Event object 'e' is undefined or missing 'range'.");
    return;
  }

  var sheet = SpreadsheetApp.getActiveSpreadsheet().getActiveSheet();
  
  if (e.range.getA1Notation() === "B1") {
    var targetWebsite = e.range.getValue();
    if (!targetWebsite) return;

    var ui = SpreadsheetApp.getUi();
    var response = ui.alert("Confirm Operation", 
                            "Would you like to start the app for " + targetWebsite + "?", 
                            ui.ButtonSet.YES_NO);

    if (response == ui.Button.NO) {
      sheet.getRange("C1").setValue("❌ Operation canceled.");
      return;
    }

    triggerGitHubActions(targetWebsite);
  }
}



function triggerGitHubActions(targetWebsite) {
  var sheet = SpreadsheetApp.getActiveSpreadsheet().getActiveSheet();
  var githubToken = PropertiesService.getScriptProperties().getProperty("GITHUB_TOKEN");
  var repoOwner = "pwhermanson";  // 🔹 REPLACE WITH YOUR GITHUB USERNAME
  var repoName = "reddit-seo-researcher";  // 🔹 REPLACE WITH YOUR GITHUB REPOSITORY NAME
  var githubApiUrl = "https://api.github.com/repos/" + repoOwner + "/" + repoName + "/dispatches";

  var payload = {
    "event_type": "trigger_reddit_scraper",
    "client_payload": {
      "target_website": targetWebsite
    }
  };

  // --- Send Cleaned Questions to KeywordInsights API ---
  Logger.log("🚀 Sending cleaned questions to KeywordInsights API for clustering...");

  var options = {  // 🔹 KeywordInsights API Request Block
    "method": "POST",
    "headers": {
        "Accept": "application/vnd.github.v3+json",
        "Authorization": "Bearer " + githubToken
    },
    "payload": JSON.stringify(payload)
  };  // ✅ Fixed: Added missing closing `}`

  try {
    var response = UrlFetchApp.fetch(githubApiUrl, options);
    var responseText = response.getContentText();
    
    // ✅ Update spreadsheet with success message
    sheet.getRange("C1").setValue("✅ Process Started for: " + targetWebsite);
    
    // ✅ Log GitHub response in Column D & E for debugging
    sheet.getRange("D1").setValue("GitHub Response:");
    sheet.getRange("E1").setValue(responseText);

  } catch (error) {
    // ❌ Update spreadsheet with error message
    sheet.getRange("C1").setValue("❌ Error Triggering GitHub Actions");
    
    // ❌ Log error details in Column D & E for debugging
    sheet.getRange("D2").setValue("Error Message:");
    sheet.getRange("E2").setValue(error.toString());
  }
}
