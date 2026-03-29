#!/usr/bin/env node
/**
 * Vercel project configurator — sets rootDirectory for chess-theater project
 * and creates a second project for synthia-3-0.
 * Reads VERCEL_TOKEN from master.env. Never echoes secrets.
 */
const fs = require('fs');
const https = require('https');
const path = require('path');

const MASTER_ENV_PATH = path.join('E:\\THE PAULI FILES', 'master.env');
const CHESS_PROJECT_ID = 'prj_T19WSaUiqLmrAewXECfctQyw4jKe';

function readEnv(filePath) {
  try {
    const content = fs.readFileSync(filePath, 'utf8');
    const env = {};
    for (const line of content.split('\n')) {
      const trimmed = line.trim();
      if (!trimmed || trimmed.startsWith('#')) continue;
      const idx = trimmed.indexOf('=');
      if (idx === -1) continue;
      const key = trimmed.slice(0, idx).trim();
      const val = trimmed.slice(idx + 1).trim().replace(/^["']|["']$/g, '');
      env[key] = val;
    }
    return env;
  } catch (e) {
    console.error('Cannot read master.env:', e.message);
    process.exit(1);
  }
}

function apiRequest(method, path, body, token) {
  return new Promise((resolve, reject) => {
    const data = body ? JSON.stringify(body) : null;
    const options = {
      hostname: 'api.vercel.com',
      port: 443,
      path,
      method,
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
        ...(data ? { 'Content-Length': Buffer.byteLength(data) } : {}),
      },
    };
    const req = https.request(options, (res) => {
      let raw = '';
      res.on('data', (c) => { raw += c; });
      res.on('end', () => {
        try { resolve({ status: res.statusCode, body: JSON.parse(raw) }); }
        catch { resolve({ status: res.statusCode, body: raw }); }
      });
    });
    req.on('error', reject);
    if (data) req.write(data);
    req.end();
  });
}

async function main() {
  const env = readEnv(MASTER_ENV_PATH);
  const token = env['VERCEL_TOKEN'];
  if (!token) { console.error('VERCEL_TOKEN not found in master.env'); process.exit(1); }
  console.log('[vercel_configure] Token loaded (' + token.length + ' chars)');

  // 1. Get current project info
  console.log('\n[1] Fetching project info...');
  const proj = await apiRequest('GET', `/v9/projects/${CHESS_PROJECT_ID}`, null, token);
  if (proj.status !== 200) {
    console.error('Project fetch failed:', proj.status, JSON.stringify(proj.body).slice(0, 200));
    process.exit(1);
  }
  const name = proj.body.name || 'unknown';
  const currentRoot = proj.body.rootDirectory || '(none)';
  const currentBranch = proj.body.link?.productionBranch || 'main';
  console.log(`   Name: ${name}`);
  console.log(`   Current rootDirectory: ${currentRoot}`);
  console.log(`   Production branch: ${currentBranch}`);

  // 2. Patch project: set rootDirectory = "chess-theater", framework = nextjs
  console.log('\n[2] Setting rootDirectory="chess-theater" on chess-theater project...');
  const patch = await apiRequest('PATCH', `/v9/projects/${CHESS_PROJECT_ID}`, {
    rootDirectory: 'chess-theater',
    framework: 'nextjs',
    installCommand: 'npm install',
    buildCommand: 'npm run build',
    outputDirectory: '.next',
  }, token);
  if (patch.status === 200) {
    console.log('   rootDirectory set to: chess-theater');
    console.log('   framework: nextjs');
  } else {
    console.error('   PATCH failed:', patch.status, JSON.stringify(patch.body).slice(0, 300));
    process.exit(1);
  }

  // 3. Create synthia-3-0 project (or update if exists)
  console.log('\n[3] Creating/updating synthia-3-0 project...');
  // Try to find existing synthia project
  const list = await apiRequest('GET', '/v9/projects?limit=100', null, token);
  let synthiaProject = null;
  if (list.status === 200 && list.body.projects) {
    synthiaProject = list.body.projects.find(p =>
      p.name === 'synthia-3-0' || p.name === 'synthia3-0' || p.name === 'synthia'
    );
  }

  if (synthiaProject) {
    // Check if it's linked to the correct repo
    const sproj = await apiRequest('GET', `/v9/projects/${synthiaProject.id}`, null, token);
    const linkedRepo = sproj.body?.link?.repo || '';
    console.log(`   Linked repo: ${linkedRepo}`);

    if (!linkedRepo.includes('archonx-os')) {
      // Wrong repo — create a fresh project linked to archonx-os
      console.log('   Wrong repo — creating new synthia-3-0 project linked to archonx-os...');
      const repoInfo = proj.body.link; // from chess-theater project (archonx-os)
      const createBody = {
        name: 'synthia-3-0-archonx',
        framework: 'nextjs',
        rootDirectory: 'synthia-3-0',
        gitRepository: repoInfo ? { repo: repoInfo.repo, type: repoInfo.type || 'github' } : undefined,
      };
      const cp = await apiRequest('POST', '/v9/projects', createBody, token);
      if (cp.status === 200 || cp.status === 201) {
        console.log(`   Created new project: ${cp.body.id} (${cp.body.name})`);
        synthiaProject = cp.body;
      } else {
        console.log(`   Create failed: ${cp.status} — ${JSON.stringify(cp.body).slice(0, 200)}`);
      }
    } else {
      // Correct repo, just patch rootDirectory
      const sp = await apiRequest('PATCH', `/v9/projects/${synthiaProject.id}`, {
        rootDirectory: 'synthia-3-0',
        framework: 'nextjs',
      }, token);
      console.log(`   Update status: ${sp.status}`);
    }
  } else {
    // Create new project linked to same repo
    const repoInfo = proj.body.link;
    const createBody = {
      name: 'synthia-3-0',
      framework: 'nextjs',
      rootDirectory: 'synthia-3-0',
      gitRepository: repoInfo ? {
        repo: repoInfo.repo,
        type: repoInfo.type || 'github',
      } : undefined,
    };
    const cp = await apiRequest('POST', '/v9/projects', createBody, token);
    if (cp.status === 200 || cp.status === 201) {
      console.log(`   Created synthia-3-0 project: ${cp.body.id}`);
    } else {
      console.log(`   Create status: ${cp.status} — ${JSON.stringify(cp.body).slice(0, 200)}`);
    }
  }

  // 4. Trigger redeployment of chess-theater from latest main commit
  console.log('\n[4] Triggering new production deployment for chess-theater...');
  // Get latest deployment to find gitSource
  const deploysList = await apiRequest('GET', `/v9/deployments?projectId=${CHESS_PROJECT_ID}&limit=1`, null, token);
  let gitCommitSha = null;
  if (deploysList.status === 200 && deploysList.body.deployments?.length) {
    // We'll create a new deployment via API
    gitCommitSha = deploysList.body.deployments[0].meta?.githubCommitSha;
  }

  // Re-fetch project to get repoId from link
  const projRe = await apiRequest('GET', `/v9/projects/${CHESS_PROJECT_ID}`, null, token);
  const repoId = projRe.body?.link?.repoId || projRe.body?.link?.id;
  const repoType = projRe.body?.link?.type || 'github';
  console.log(`   repoId: ${repoId}, type: ${repoType}`);

  const deployBody = {
    name: name,
    project: CHESS_PROJECT_ID,
    target: 'production',
    gitSource: {
      type: repoType,
      repo: 'executiveusa/archonx-os',
      ref: 'main',
      ...(repoId ? { repoId: String(repoId) } : {}),
    },
  };
  const deploy = await apiRequest('POST', '/v13/deployments', deployBody, token);
  if (deploy.status === 200 || deploy.status === 201) {
    const url = deploy.body.url || deploy.body.alias?.[0] || 'pending';
    console.log(`   Deployment created: https://${url}`);
    console.log(`   Deployment ID: ${deploy.body.id}`);
    console.log(`   Status: ${deploy.body.readyState || deploy.body.status}`);
  } else {
    console.log(`   Deploy status: ${deploy.status}`);
    console.log(`   Response: ${JSON.stringify(deploy.body).slice(0, 400)}`);
  }

  // 5. Trigger synthia-3-0 deployment
  const SYNTHIA_PROJECT_ID = synthiaProject ? (synthiaProject.id || synthiaProject.body?.id) : null;
  if (SYNTHIA_PROJECT_ID) {
    console.log('\n[5] Triggering new production deployment for synthia-3-0...');
    const sproj = await apiRequest('GET', `/v9/projects/${SYNTHIA_PROJECT_ID}`, null, token);
    const srepoId = sproj.body?.link?.repoId || sproj.body?.link?.id;
    const srepoType = sproj.body?.link?.type || 'github';
    console.log(`   repoId: ${srepoId}, type: ${srepoType}`);
    if (srepoId) {
      const sdeploy = await apiRequest('POST', '/v13/deployments', {
        name: 'synthia-3-0',
        project: SYNTHIA_PROJECT_ID,
        target: 'production',
        gitSource: { type: srepoType, repo: 'executiveusa/archonx-os', ref: 'main', repoId: String(srepoId) },
      }, token);
      if (sdeploy.status === 200 || sdeploy.status === 201) {
        console.log(`   Deployment created: https://${sdeploy.body.url}`);
        console.log(`   Status: ${sdeploy.body.readyState || sdeploy.body.status}`);
      } else {
        console.log(`   Deploy status: ${sdeploy.status}: ${JSON.stringify(sdeploy.body).slice(0, 300)}`);
      }
    } else {
      console.log('   No repoId found for synthia project — link it to GitHub in Vercel dashboard first.');
    }
  }

  console.log('\n[vercel_configure] Done. Check https://vercel.com/dashboard for deployment progress.');
}

main().catch(e => { console.error(e); process.exit(1); });
