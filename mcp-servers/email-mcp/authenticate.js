#!/usr/bin/env node
/**
 * Gmail OAuth Authentication Script
 * 
 * Run this once to authenticate with Gmail API and generate token.json
 * 
 * Usage:
 *   1. Download credentials.json from Google Cloud Console
 *   2. Run: node authenticate.js
 *   3. Open the URL in browser and authorize
 *   4. Paste the authorization code
 *   5. token.json will be created
 */

import { google } from 'googleapis';
import fs from 'fs';
import path from 'path';
import readline from 'readline';

const SCOPES = ['https://www.googleapis.com/auth/gmail.send'];
const CREDENTIALS_PATH = process.env.GMAIL_CREDENTIALS || 'credentials.json';
const TOKEN_PATH = process.env.GMAIL_TOKEN || 'token.json';

/**
 * Get credentials from file
 */
function loadCredentials() {
  const content = fs.readFileSync(CREDENTIALS_PATH, 'utf8');
  return JSON.parse(content);
}

/**
 * Authorize using OAuth2 and return credentials
 */
async function authorize() {
  const credentials = loadCredentials();
  const { client_secret, client_id, redirect_uris } = credentials.web || credentials.installed;
  
  const oAuth2Client = new google.auth.OAuth2(
    client_id,
    client_secret,
    redirect_uris[0]
  );
  
  // Check for existing token
  if (fs.existsSync(TOKEN_PATH)) {
    const token = fs.readFileSync(TOKEN_PATH, 'utf8');
    oAuth2Client.setCredentials(JSON.parse(token));
    console.log('✅ Token already exists. Refreshing...');
    
    try {
      const { credentials: newCredentials } = await oAuth2Client.refreshAccessToken();
      fs.writeFileSync(TOKEN_PATH, JSON.stringify(newCredentials, null, 2));
      console.log('✅ Token refreshed successfully!');
      return oAuth2Client;
    } catch (error) {
      console.log('⚠️ Token refresh failed. Re-authenticating...');
    }
  }
  
  // Generate auth URL
  const authUrl = oAuth2Client.generateAuthUrl({
    access_type: 'offline',
    scope: SCOPES,
  });
  
  console.log('📧 Gmail OAuth Authentication');
  console.log('============================\n');
  console.log('Authorize this app by visiting this url:');
  console.log(authUrl);
  console.log('\nAfter authorization, paste the code below:\n');
  
  const rl = readline.createInterface({
    input: process.stdin,
    output: process.stdout,
  });
  
  return new Promise((resolve, reject) => {
    rl.question('Enter authorization code: ', async (code) => {
      rl.close();
      
      try {
        const { tokens } = await oAuth2Client.getToken(code);
        oAuth2Client.setCredentials(tokens);
        
        // Save token
        fs.writeFileSync(TOKEN_PATH, JSON.stringify(tokens, null, 2));
        console.log(`\n✅ Token saved to ${TOKEN_PATH}`);
        console.log('You can now use the Email MCP server!');
        
        resolve(oAuth2Client);
      } catch (error) {
        console.error('❌ Error retrieving tokens:', error.message);
        reject(error);
      }
    });
  });
}

// Run authentication
authorize().catch(console.error);
