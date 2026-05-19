// Google Apps Script bridge: Gmail -> GitHub repository_dispatch
//
// Install manually in script.google.com.
// Required script properties:
// - GITHUB_TOKEN: fine-grained token allowed to dispatch workflows/repository events for TomasDelon/nabla-agent-lab
// - GITHUB_REPO: TomasDelon/nabla-agent-lab
//
// Add a time trigger every 5 minutes or every 10 minutes.

const DEFAULT_REPO = 'TomasDelon/nabla-agent-lab';
const DISPATCH_EVENT_TYPE = 'nabla_email_prompt';
const PROCESSED_LABEL = 'NABLA_DISPATCHED';

function pollNablaPromptEmails() {
  const props = PropertiesService.getScriptProperties();
  const token = props.getProperty('GITHUB_TOKEN');
  const repo = props.getProperty('GITHUB_REPO') || DEFAULT_REPO;

  if (!token) {
    throw new Error('Missing script property GITHUB_TOKEN');
  }

  const label = getOrCreateLabel_(PROCESSED_LABEL);
  const query = 'subject:"[NABLA][PROMPT]" newer_than:7d -label:' + PROCESSED_LABEL;
  const threads = GmailApp.search(query, 0, 10);

  for (const thread of threads) {
    const messages = thread.getMessages();
    const message = messages[messages.length - 1];
    const subject = message.getSubject();
    const body = message.getPlainBody();

    const payload = parsePromptEmail_(subject, body, repo);
    if (!payload) {
      thread.addLabel(label);
      continue;
    }

    dispatchToGitHub_(repo, token, payload);
    thread.addLabel(label);
  }
}

function parsePromptEmail_(subject, body, fallbackRepo) {
  const runMatch = subject.match(/\[RUN:([^\]]+)\]/);
  const builderMatch = subject.match(/\[BUILDER-([^\]]+)\]/);

  if (!runMatch || !builderMatch) {
    return null;
  }

  const runId = runMatch[1].trim();
  const builder = 'builder-' + builderMatch[1].toLowerCase().trim();
  const fields = parseYamlLike_(body);

  return {
    kind: 'prompt',
    repo: fields.repo || fallbackRepo,
    run_id: fields.run_id || runId,
    builder: fields.builder || builder,
    base_branch: fields.base_branch || 'main',
    branch: fields.branch || ('agent/' + runId),
    report_path: fields.report_path || ('.nabla-agent/runs/' + runId),
    allowed_paths: fields.allowed_paths || ['src/**', 'tests/**'],
    forbidden_paths: fields.forbidden_paths || ['.github/**', 'package.json'],
    task: fields.task || body,
    acceptance: fields.acceptance || ['npm test passes', 'diff touches only allowed paths', 'report files are generated'],
    source_email_subject: subject,
  };
}

function parseYamlLike_(body) {
  const result = {};
  const lines = body.split(/\r?\n/);
  let currentKey = null;
  let collectingBlock = false;
  let block = [];
  let collectingList = false;

  function flushBlock() {
    if (currentKey && collectingBlock) {
      result[currentKey] = block.join('\n').trim();
    }
    currentKey = null;
    collectingBlock = false;
    collectingList = false;
    block = [];
  }

  for (const line of lines) {
    const keyBlock = line.match(/^([a-zA-Z_]+):\s*\|\s*$/);
    if (keyBlock) {
      flushBlock();
      currentKey = keyBlock[1];
      collectingBlock = true;
      block = [];
      continue;
    }

    const keyList = line.match(/^([a-zA-Z_]+):\s*$/);
    if (keyList) {
      flushBlock();
      currentKey = keyList[1];
      collectingList = true;
      result[currentKey] = [];
      continue;
    }

    const listItem = line.match(/^\s*-\s*(.+)$/);
    if (collectingList && currentKey && listItem) {
      result[currentKey].push(stripQuotes_(listItem[1].trim()));
      continue;
    }

    const keyValue = line.match(/^([a-zA-Z_]+):\s*(.+)$/);
    if (keyValue) {
      flushBlock();
      result[keyValue[1]] = stripQuotes_(keyValue[2].trim());
      continue;
    }

    if (collectingBlock) {
      block.push(line.replace(/^\s{2}/, ''));
    }
  }

  flushBlock();
  return result;
}

function stripQuotes_(value) {
  return value.replace(/^['"]|['"]$/g, '');
}

function dispatchToGitHub_(repo, token, payload) {
  const url = 'https://api.github.com/repos/' + repo + '/dispatches';
  const response = UrlFetchApp.fetch(url, {
    method: 'post',
    contentType: 'application/json',
    headers: {
      Authorization: 'Bearer ' + token,
      Accept: 'application/vnd.github+json',
      'X-GitHub-Api-Version': '2022-11-28',
    },
    payload: JSON.stringify({
      event_type: DISPATCH_EVENT_TYPE,
      client_payload: payload,
    }),
    muteHttpExceptions: true,
  });

  const code = response.getResponseCode();
  if (code < 200 || code >= 300) {
    throw new Error('GitHub dispatch failed: ' + code + ' ' + response.getContentText());
  }
}

function getOrCreateLabel_(name) {
  return GmailApp.getUserLabelByName(name) || GmailApp.createLabel(name);
}
