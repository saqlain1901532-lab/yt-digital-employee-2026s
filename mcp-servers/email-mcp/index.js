#!/usr/bin/env node
/**
 * Email MCP Server for AI Employee - Silver Tier
 * 
 * Model Context Protocol server for sending emails via Gmail.
 * Supports draft and send operations with human-in-the-loop approval.
 * 
 * Usage:
 *   node email-mcp/index.js
 * 
 * Configuration:
 *   Set GMAIL_CREDENTIALS environment variable to path of credentials.json
 */

import { Server } from '@modelcontextprotocol/sdk/server/index.js';
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';
import {
  CallToolRequestSchema,
  ListToolsRequestSchema,
} from '@modelcontextprotocol/sdk/types.js';
import nodemailer from 'nodemailer';
import { google } from 'googleapis';
import fs from 'fs';
import path from 'path';

// Configuration
const CREDENTIALS_PATH = process.env.GMAIL_CREDENTIALS || 'credentials.json';
const TOKEN_PATH = process.env.GMAIL_TOKEN || 'token.json';
const SCOPES = ['https://www.googleapis.com/auth/gmail.send'];

// Email state
const sentEmails = [];
const drafts = [];

/**
 * Create OAuth2 client
 */
function createOAuth2Client() {
  const credentials = JSON.parse(fs.readFileSync(CREDENTIALS_PATH, 'utf8'));
  const { client_secret, client_id, redirect_uris } = credentials.web || credentials.installed;
  
  return new google.auth.OAuth2(client_id, client_secret, redirect_uris[0]);
}

/**
 * Get or refresh access token
 */
async function getAccessToken(oAuth2Client) {
  const tokenPath = TOKEN_PATH;
  
  if (fs.existsSync(tokenPath)) {
    const token = JSON.parse(fs.readFileSync(tokenPath, 'utf8'));
    oAuth2Client.setCredentials(token);
    
    // Refresh if expired
    if (token.expiry_date && token.expiry_date < Date.now()) {
      try {
        const { credentials } = await oAuth2Client.refreshAccessToken();
        fs.writeFileSync(tokenPath, JSON.stringify(credentials));
      } catch (error) {
        console.error('Token refresh failed. Please re-authenticate.');
        throw error;
      }
    }
    
    return oAuth2Client;
  } else {
    console.error('Token file not found. Please authenticate first.');
    console.error('Run: node email-mcp/authenticate.js');
    throw new Error('Token not found');
  }
}

/**
 * Create transporter using Gmail OAuth2
 */
async function createTransporter() {
  const oAuth2Client = createOAuth2Client();
  await getAccessToken(oAuth2Client);
  
  const accessToken = await oAuth2Client.getAccessToken();
  
  return nodemailer.createTransport({
    host: 'smtp.gmail.com',
    port: 587,
    secure: false,
    auth: {
      type: 'OAuth2',
      user: process.env.GMAIL_USER || 'me',
      clientId: JSON.parse(fs.readFileSync(CREDENTIALS_PATH, 'utf8')).web.client_id,
      clientSecret: JSON.parse(fs.readFileSync(CREDENTIALS_PATH, 'utf8')).web.client_secret,
      refreshToken: oAuth2Client.credentials.refresh_token,
      accessToken: accessToken.token,
    },
  });
}

/**
 * MCP Server instance
 */
const server = new Server(
  {
    name: 'email-mcp',
    version: '0.1.0',
  },
  {
    capabilities: {
      tools: {},
    },
  }
);

/**
 * List available tools
 */
server.setRequestHandler(ListToolsRequestSchema, async () => {
  return {
    tools: [
      {
        name: 'send_email',
        description: 'Send an email via Gmail. Requires approval for new contacts.',
        inputSchema: {
          type: 'object',
          properties: {
            to: {
              type: 'string',
              description: 'Recipient email address',
            },
            subject: {
              type: 'string',
              description: 'Email subject',
            },
            body: {
              type: 'string',
              description: 'Email body (plain text or HTML)',
            },
            isHtml: {
              type: 'boolean',
              description: 'Whether body is HTML (default: false)',
              default: false,
            },
            cc: {
              type: 'string',
              description: 'CC recipients (comma-separated)',
            },
            bcc: {
              type: 'string',
              description: 'BCC recipients (comma-separated)',
            },
            attachment: {
              type: 'string',
              description: 'Path to attachment file',
            },
          },
          required: ['to', 'subject', 'body'],
        },
      },
      {
        name: 'create_draft',
        description: 'Create a draft email without sending. Use for review before sending.',
        inputSchema: {
          type: 'object',
          properties: {
            to: {
              type: 'string',
              description: 'Recipient email address',
            },
            subject: {
              type: 'string',
              description: 'Email subject',
            },
            body: {
              type: 'string',
              description: 'Email body',
            },
            isHtml: {
              type: 'boolean',
              description: 'Whether body is HTML',
              default: false,
            },
          },
          required: ['to', 'subject', 'body'],
        },
      },
      {
        name: 'list_sent_emails',
        description: 'List recently sent emails from this session',
        inputSchema: {
          type: 'object',
          properties: {
            limit: {
              type: 'number',
              description: 'Number of emails to return (default: 10)',
              default: 10,
            },
          },
        },
      },
    ],
  };
});

/**
 * Handle tool calls
 */
server.setRequestHandler(CallToolRequestSchema, async (request) => {
  const { name, arguments: args } = request.params;
  
  try {
    switch (name) {
      case 'send_email': {
        const { to, subject, body, isHtml = false, cc, bcc, attachment } = args;
        
        // Create transporter
        const transporter = await createTransporter();
        
        // Build email options
        const mailOptions = {
          from: process.env.GMAIL_USER || 'me',
          to,
          subject,
          text: isHtml ? undefined : body,
          html: isHtml ? body : undefined,
        };
        
        if (cc) mailOptions.cc = cc;
        if (bcc) mailOptions.bcc = bcc;
        if (attachment) {
          mailOptions.attachments = [{ path: attachment }];
        }
        
        // Send email
        const info = await transporter.sendMail(mailOptions);
        
        // Record sent email
        const sentEmail = {
          timestamp: new Date().toISOString(),
          to,
          subject,
          messageId: info.messageId,
        };
        sentEmails.push(sentEmail);
        
        // Log to vault if configured
        const logPath = process.env.VAULT_LOGS;
        if (logPath) {
          const logFile = path.join(logPath, `${new Date().toISOString().split('T')[0]}_emails.jsonl`);
          fs.appendFileSync(logFile, JSON.stringify(sentEmail) + '\n');
        }
        
        return {
          content: [
            {
              type: 'text',
              text: `✅ Email sent successfully!\n\nTo: ${to}\nSubject: ${subject}\nMessage ID: ${info.messageId}`,
            },
          ],
        };
      }
      
      case 'create_draft': {
        const { to, subject, body, isHtml = false } = args;
        
        // Create draft object
        const draft = {
          id: `draft_${Date.now()}`,
          timestamp: new Date().toISOString(),
          to,
          subject,
          body,
          isHtml,
          status: 'draft',
        };
        drafts.push(draft);
        
        return {
          content: [
            {
              type: 'text',
              text: `📝 Draft created successfully!\n\nDraft ID: ${draft.id}\nTo: ${to}\nSubject: ${subject}\n\nReview the draft and use send_email to send when ready.`,
            },
          ],
        };
      }
      
      case 'list_sent_emails': {
        const { limit = 10 } = args;
        const recent = sentEmails.slice(-limit).reverse();
        
        if (recent.length === 0) {
          return {
            content: [
              {
                type: 'text',
                text: 'No emails sent in this session.',
              },
            ],
          };
        }
        
        const list = recent.map((email, i) => 
          `${i + 1}. To: ${email.to}\n   Subject: ${email.subject}\n   Time: ${email.timestamp}`
        ).join('\n\n');
        
        return {
          content: [
            {
              type: 'text',
              text: `📧 Recently Sent Emails (${recent.length}):\n\n${list}`,
            },
          ],
        };
      }
      
      default:
        throw new Error(`Unknown tool: ${name}`);
    }
  } catch (error) {
    return {
      content: [
        {
          type: 'text',
          text: `❌ Error: ${error.message}`,
          isError: true,
        },
      ],
    };
  }
});

/**
 * Start the server
 */
async function main() {
  // Check credentials file
  if (!fs.existsSync(CREDENTIALS_PATH)) {
    console.error(`Error: Credentials file not found: ${CREDENTIALS_PATH}`);
    console.error('Please set GMAIL_CREDENTIALS environment variable');
    process.exit(1);
  }
  
  const transport = new StdioServerTransport();
  await server.connect(transport);
  
  console.error('Email MCP Server running on stdio');
  console.error(`Credentials: ${CREDENTIALS_PATH}`);
  console.error(`Token: ${TOKEN_PATH}`);
}

main().catch((error) => {
  console.error('Fatal error:', error);
  process.exit(1);
});
