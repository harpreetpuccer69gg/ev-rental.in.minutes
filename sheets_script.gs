/**
 * Main function to transfer leads and send summary emails.
 * Set this to run on a Time-Driven trigger (1 hour).
 */
function onLeadSubmit() {
  const masterSheet = SpreadsheetApp.getActiveSpreadsheet();
  const allSheets = masterSheet.getSheets();
  const leadsSheet = allSheets.find(s => s.getName().trim() === 'Leads');
  const vendorMap = allSheets.find(s => s.getName().trim() === 'Vendor_Map');

  if (!leadsSheet || !vendorMap) { 
    Logger.log('Required sheets (Leads or Vendor_Map) not found'); 
    return; 
  }

  const allData = leadsSheet.getDataRange().getValues();
  const ourHeaders = allData[0];

  // Ensure "Transferred" and "Email Sent" columns exist
  let transferCol = ourHeaders.findIndex(h => h.toString().trim() === 'Transferred');
  if (transferCol === -1) {
    transferCol = ourHeaders.length;
    leadsSheet.getRange(1, transferCol + 1).setValue('Transferred');
  }

  let emailCol = ourHeaders.findIndex(h => h.toString().trim() === 'Email Sent');
  if (emailCol === -1) {
    emailCol = transferCol + 1;
    leadsSheet.getRange(1, emailCol + 1).setValue('Email Sent');
  }

  // --- ADDITION 1: Find or create Status column (col P = index 15) ---
  let statusCol = ourHeaders.findIndex(h => h.toString().trim().toLowerCase() === 'status');
  if (statusCol === -1) {
    statusCol = 15; // column P
    leadsSheet.getRange(1, statusCol + 1).setValue('Status');
  }
  // --- END ADDITION 1 ---

  const mapData = vendorMap.getDataRange().getValues();

  // Helper: Normalize vendor names for matching
  function normalizeVendor(name) {
    if (!name) return "";
    const n = name.toString().trim().toLowerCase();
    if (n === 'voltup' || n === 'volt up')                       return 'voltup';
    if (n === 'gogreen' || n === 'go green')                     return 'gogreen';
    if (n === 'eco ev' || n === 'ecoev')                         return 'ecoev';
    if (n === 'yuwwaa' || n === 'yuvwaaspeed' || n === 'yuvwaa') return 'yuvwaa';
    if (n === 'bijliride' || n === 'bijli ride')                  return 'bijliride';
    if (n === 'e-went' || n === 'ewent')                         return 'ewent';
    if (n === 'yugorides' || n === 'yugo')                       return 'yugorides';
    return n.replace(/\s+/g, '').replace(/-/g, '');
  }

  // Helper: Map Lead data to Vendor sheet headers
  function getValueForHeader(header, row) {
    const h = header.toString().trim().toLowerCase();
    if (h === 'date' || h === 'timestamp') {
      if (!row[0]) return '';
      try { return Utilities.formatDate(new Date(row[0]), Session.getScriptTimeZone(), 'dd MMM yyyy hh:mm a'); } catch(e) { return row[0].toString(); }
    }
    if (h === 'rider name' || h === 'name')                      return row[1];
    if (h === 'phone' || h === 'rider phone' || h === 'mobile')  return row[2];
    if (h === 'city')                                             return row[3];
    if (h === 'language')                                         return row[4];
    if (h === 'budget' || h === 'budget range')                   return row[5];
    if (h === 'vendor')                                           return row[7];
    if (h === 'make' || h === 'model' || h === 'vehicle')         return row[8];
    if (h === 'type')                                             return row[9];
    if (h === 'rental/week' || h === 'rent' || h === 'rental')    return row[10];
    if (h === 'security deposit' || h === 'deposit')              return row[11];
    if (h === 'refundable deposit' || h === 'refundable')         return row[12];
    if (h === 'spoc name')                                        return row[13];
    if (h === 'spoc phone')                                       return row[14];
    if (h === 'status' || h === 'conversion status')              return 'Pending';
    if (h === 'conversion status')                                 return 'Pending';
    return '';
  }

  // Helper: Format and send the summary email
  function sendSummaryEmail(vendorName, emailAddresses, cityCountMap, sheetLink) {
    if (!emailAddresses) return false;
    const emails = emailAddresses.split(',').map(e => e.trim()).filter(e => e);
    if (emails.length === 0) return false;

    const total = Object.values(cityCountMap).reduce((a, b) => a + b, 0);
    const now = new Date();
    const timeStr = Utilities.formatDate(now, Session.getScriptTimeZone(), 'dd MMM yyyy hh:mm a');

    const subject = vendorName + ' - ' + total + ' New Lead(s) | ' + timeStr + ' | Flipkart Minutes';

    let cityLines = '';
    Object.keys(cityCountMap).sort().forEach(city => {
      cityLines += `  - ${city}: ${cityCountMap[city]} lead(s)\n`;
    });

    const sheetLine = sheetLink ? '\nView your leads sheet here:\n' + sheetLink + '\n' : '';

    const body = `Hi ${vendorName} Team,

You have received ${total} new lead(s) in the last hour from Flipkart Minutes EV Assist.
${sheetLine}
----------------------------------------
LEADS SUMMARY (City-wise)
----------------------------------------
${cityLines}
Total New Leads : ${total}
----------------------------------------

Please update the Status column after contacting each rider within 24 hours.

- Flipkart Minutes EV Assist
https://ev-rental-in-minutes.onrender.com`;

    emails.forEach(email => {
      try {
        GmailApp.sendEmail(email, subject, body);
        Logger.log('Email sent to: ' + email);
      } catch(e) {
        Logger.log('Email error for ' + email + ': ' + e.message);
      }
    });
    return true;
  }

  // STEP 1: Transfer rows to individual vendor sheets
  for (let i = 1; i < allData.length; i++) {
    const row = allData[i];
    const transferred = (row[transferCol] || '').toString().trim().toUpperCase();
    if (transferred === 'YES') continue;

    const vendorName = (row[7] || '').toString().trim();
    if (!vendorName) continue;

    // Fix: if manually written row has no timestamp, set current time
    if (!row[0]) {
      leadsSheet.getRange(i + 1, 1).setValue(new Date());
    }

    // --- ADDITION 1: Set Status = Pending for new leads ---
    const currentStatus = (row[statusCol] || '').toString().trim();
    if (!currentStatus) {
      leadsSheet.getRange(i + 1, statusCol + 1).setValue('Pending');
    }
    // --- END ADDITION 1 ---

    let vendorSheetId = null;
    let targetTab = 'Leads';
    let vendorEmail = '';

    for (let j = 1; j < mapData.length; j++) {
      if (normalizeVendor(mapData[j][0]) === normalizeVendor(vendorName)) {
        vendorSheetId = mapData[j][1].toString().trim();
        targetTab     = (mapData[j][3] || 'Leads').toString().trim();
        vendorEmail   = (mapData[j][2] || '').toString().trim();
        break;
      }
    }

    if (vendorSheetId) {
      try {
        const vendorSpreadsheet = SpreadsheetApp.openById(vendorSheetId);
        let vendorSheet = vendorSpreadsheet.getSheetByName(targetTab);
        if (!vendorSheet) {
          vendorSheet = vendorSpreadsheet.insertSheet(targetTab);
          vendorSheet.appendRow(ourHeaders.slice(0, transferCol));
        }
        const vendorHeaders = vendorSheet.getRange(1, 1, 1, vendorSheet.getLastColumn()).getValues()[0];
        const mappedRow = vendorHeaders.map(h => getValueForHeader(h, row));
        vendorSheet.appendRow(mappedRow);

        // --- ADDITION 2: Share vendor sheet with editor access every time ---
        if (vendorEmail) {
          const emails = vendorEmail.split(',').map(e => e.trim()).filter(e => e);
          emails.forEach(email => {
            try {
              vendorSpreadsheet.addEditor(email);
              Logger.log('Shared sheet with: ' + email);
            } catch(shareErr) {
              Logger.log('Share error for ' + email + ': ' + shareErr.message);
            }
          });
        }
        // --- END ADDITION 2 ---

        leadsSheet.getRange(i + 1, transferCol + 1).setValue('YES');
      } catch(err) {
        Logger.log('Sheet ERROR for ' + vendorName + ': ' + err.message);
        leadsSheet.getRange(i + 1, transferCol + 1).setValue('ERROR');
      }
    }
  }

  // STEP 2: Batch email summary
  const freshData = leadsSheet.getDataRange().getValues();
  const vendorBatch = {};

  for (let i = 1; i < freshData.length; i++) {
    const row = freshData[i];
    if (row[emailCol] === 'YES') continue;

    const vendorName = (row[7] || '').toString().trim();
    const city       = (row[3] || '').toString().trim();
    if (!vendorName || !city) continue;

    const vKey = normalizeVendor(vendorName);

    if (!vendorBatch[vKey]) {
      let vEmail = '';
      let vDisplayName = vendorName;
      let vSheetLink = '';
      for (let j = 1; j < mapData.length; j++) {
        if (normalizeVendor(mapData[j][0]) === vKey) {
          vEmail = mapData[j][2].toString().trim();
          vDisplayName = mapData[j][0].toString().trim();
          vSheetLink = (mapData[j][4] || '').toString().trim();
          break;
        }
      }
      if (!vEmail) continue;
      vendorBatch[vKey] = { name: vDisplayName, email: vEmail, sheetLink: vSheetLink, cityCount: {}, rowIndices: [] };
    }

    vendorBatch[vKey].cityCount[city] = (vendorBatch[vKey].cityCount[city] || 0) + 1;
    vendorBatch[vKey].rowIndices.push(i + 1);
  }

  for (const vKey in vendorBatch) {
    const { name, email, sheetLink, cityCount, rowIndices } = vendorBatch[vKey];
    if (sendSummaryEmail(name, email, cityCount, sheetLink)) {
      rowIndices.forEach(rowNum => {
        leadsSheet.getRange(rowNum, emailCol + 1).setValue('YES');
      });
    }
  }

  // --- ADDITION 3: Pull Status from vendor sheets and update EV_Assist Leads ---
  syncStatusFromVendors(leadsSheet, vendorMap, statusCol, transferCol);
  // --- END ADDITION 3 ---
}

/**
 * ADDITION 3: Pulls Status from each vendor sheet and updates EV_Assist Leads
 * Matches by Rider Phone (col C = index 2)
 */
function syncStatusFromVendors(leadsSheet, vendorMap, statusCol, transferCol) {
  const mapData = vendorMap.getDataRange().getValues();
  const leadsData = leadsSheet.getDataRange().getValues();

  // Build phone → row index map from master sheet
  const phoneToRow = {};
  for (let i = 1; i < leadsData.length; i++) {
    const phone = (leadsData[i][2] || '').toString().trim();
    if (phone) phoneToRow[phone] = i + 1; // 1-based row number
  }

  for (let j = 1; j < mapData.length; j++) {
    const vendorSheetId = (mapData[j][1] || '').toString().trim();
    const targetTab     = (mapData[j][3] || 'Leads').toString().trim();
    if (!vendorSheetId) continue;

    try {
      const vendorSpreadsheet = SpreadsheetApp.openById(vendorSheetId);
      const vendorSheet = vendorSpreadsheet.getSheetByName(targetTab);
      if (!vendorSheet) continue;

      const vendorData = vendorSheet.getDataRange().getValues();
      const vendorHeaders = vendorData[0];

      // Find Phone and Status columns in vendor sheet
      const vPhoneCol = vendorHeaders.findIndex(h => h.toString().trim().toLowerCase() === 'phone');
      const vStatusCol = vendorHeaders.findIndex(h => h.toString().trim().toLowerCase() === 'status');
      if (vPhoneCol === -1 || vStatusCol === -1) continue;

      for (let k = 1; k < vendorData.length; k++) {
        const vPhone  = (vendorData[k][vPhoneCol] || '').toString().trim();
        const vStatus = (vendorData[k][vStatusCol] || '').toString().trim();

        if (!vPhone || !vStatus || vStatus === 'Pending' || vStatus === 'New Lead' || vStatus === '') continue;

        if (phoneToRow[vPhone]) {
          leadsSheet.getRange(phoneToRow[vPhone], statusCol + 1).setValue(vStatus);
          Logger.log('Status synced for phone ' + vPhone + ': ' + vStatus);
        }
      }
    } catch(err) {
      Logger.log('Sync error for vendor row ' + j + ': ' + err.message);
    }
  }
}

/**
 * Creates a trigger to run the lead submission script every hour.
 */
function createTrigger() {
  const triggers = ScriptApp.getProjectTriggers();
  triggers.forEach(t => ScriptApp.deleteTrigger(t));
  
  ScriptApp.newTrigger('onLeadSubmit')
    .timeBased()
    .everyHours(1)
    .create();
    
  Logger.log('Trigger created successfully.');
}
