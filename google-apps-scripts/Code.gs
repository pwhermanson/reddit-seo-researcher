// ===============================================
// 📌 How It Works - Google Apps Script
// ===============================================
// 1️⃣ User enters a target website into cell B1 in Google Sheets.
// 2️⃣ Script detects the change and prevents duplicate triggers for the same website.
// 3️⃣ Automatically grants "Editor" access to the Reddit scraper service account.
// 4️⃣ Prompts the user to confirm before starting the process.
// 5️⃣ If confirmed, the script sends a request to GitHub Actions to trigger `main.py`.
// 6️⃣ GitHub Actions runs the Reddit SEO Researcher script with the provided target website.
// 7️⃣ The script scrapes the website, analyzes the data with OpenAI, and updates Google Sheets.
// 8️⃣ The script logs GitHub response or errors for debugging.
// ===============================================


function customOnEdit(e) {
  if (!e || !e.range) {
    Logger.log("⚠️ Script manually executed. No edit detected.");
    return;
  }

  var sheet = SpreadsheetApp.getActiveSpreadsheet().getActiveSheet();

  // ✅ Ensure the edit was in B1 and only runs once per change
  if (e.range.getA1Notation() === "B1") {
    var targetWebsite = e.range.getValue();
    if (!targetWebsite) return;

    // ✅ Prevent multiple triggers for the same site
    var scriptProperties = PropertiesService.getScriptProperties();
    var lastTriggered = scriptProperties.getProperty("LAST_TRIGGERED_SITE");

    if (lastTriggered === targetWebsite) {
      Logger.log("⚠️ Duplicate trigger prevented.");
      return;
    }

    scriptProperties.setProperty("LAST_TRIGGERED_SITE", targetWebsite);

    // ✅ NEW: Automatically share the spreadsheet with the service account
    shareSpreadsheetWithServiceAccount();

    // ✅ Show confirmation prompt only once
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
  
  // ✅ Retrieve GitHub Token from script properties
  var githubToken = PropertiesService.getScriptProperties().getProperty("GITHUB_TOKEN");
  
  // ✅ Define GitHub repository details
  var repoOwner = "pwhermanson";  // 🔹 REPLACE WITH YOUR GITHUB USERNAME
  var repoName = "reddit-seo-researcher";  // 🔹 REPLACE WITH YOUR GITHUB REPOSITORY NAME
  var githubApiUrl = "https://api.github.com/repos/" + repoOwner + "/" + repoName + "/dispatches";

  var payload = {
    "event_type": "trigger_reddit_scraper", // ✅ Matches GitHub Actions event trigger
    "client_payload": {
      "target_website": targetWebsite
    }
  };

  // ✅ Log request details for debugging
  Logger.log("🚀 Sending request to GitHub Actions...");
  Logger.log("🔹 Target Website: " + targetWebsite);
  Logger.log("🔹 API URL: " + githubApiUrl);
  
  var options = {
    "method": "POST",
    "headers": {
        "Accept": "application/vnd.github.v3+json",
        "Authorization": "Bearer " + githubToken
    },
    "payload": JSON.stringify(payload)
  };

  try {
    // ✅ Send request to GitHub Actions
    var response = UrlFetchApp.fetch(githubApiUrl, options);
    var responseText = response.getContentText();
    
    // ✅ Check for successful GitHub Actions trigger
    if (response.getResponseCode() === 204) {
      sheet.getRange("C1").setValue("✅ Process Started for: " + targetWebsite);
      Logger.log("✅ GitHub Actions triggered successfully.");
    } else {
      sheet.getRange("C1").setValue("⚠️ Unexpected Response from GitHub.");
      Logger.log("⚠️ GitHub Response: " + responseText);
    }
    
    // ✅ Store GitHub API response in Google Sheets for debugging
    sheet.getRange("D1").setValue("GitHub Response:");
    sheet.getRange("E1").setValue(responseText);

  } catch (error) {
    // ❌ Handle API errors and log them in Google Sheets
    sheet.getRange("C1").setValue("❌ Error Triggering GitHub Actions");
    sheet.getRange("D2").setValue("Error Message:");
    sheet.getRange("E2").setValue(error.toString());
    Logger.log("❌ Error Triggering GitHub Actions: " + error.toString());
  }
}

function triggerKeywordInsightsAPI(targetWebsite) {
  // ✅ Ensure KeywordInsights API runs after GitHub Actions completes
  Logger.log("🚀 Sending cleaned questions to KeywordInsights API for clustering...");

  var keywordInsightsApiUrl = "https://api.keywordinsights.ai/cluster";
  var keywordInsightsPayload = {
    "event_type": "trigger_keyword_clustering",
    "client_payload": {
      "target_website": targetWebsite
    }
  };

  var keywordInsightsOptions = {
    "method": "POST",
    "headers": {
        "Accept": "application/json",
        "Authorization": "Bearer " + PropertiesService.getScriptProperties().getProperty("KEYWORDINSIGHTS_API_KEY")
    },
    "payload": JSON.stringify(keywordInsightsPayload)
  };

  try {
    var kiResponse = UrlFetchApp.fetch(keywordInsightsApiUrl, keywordInsightsOptions);
    var kiResponseText = kiResponse.getContentText();
    Logger.log("✅ KeywordInsights API Response: " + kiResponseText);
  } catch (error) {
    Logger.log("❌ Error Triggering KeywordInsights API: " + error.toString());
  }
}
