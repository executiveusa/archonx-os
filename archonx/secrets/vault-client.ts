import * as fs from 'fs';
import * as path from 'path';

export interface VaultHealthResult {
  status: 'ok' | 'degraded' | 'error';
  vaultExists: boolean;
  masterKeySet: boolean;
  message: string;
}

/**
 * Checks whether the ArchonX vault is accessible and configured.
 * Vault file: .archonx/vault.bin (written by archonx/security/vault.py)
 * Master key: ARCHONX_MASTER_KEY environment variable
 */
export function checkVaultHealth(): VaultHealthResult {
  const vaultPath = path.resolve(process.cwd(), '.archonx/vault.bin');

  let vaultExists: boolean;
  try {
    vaultExists = fs.existsSync(vaultPath);
  } catch (err) {
    return {
      status: 'error',
      vaultExists: false,
      masterKeySet: false,
      message: `Failed to access vault path: ${(err as Error).message}`,
    };
  }

  const masterKeySet = Boolean(process.env.ARCHONX_MASTER_KEY);

  if (vaultExists && masterKeySet) {
    return {
      status: 'ok',
      vaultExists,
      masterKeySet,
      message: 'Vault is accessible and master key is configured.',
    };
  }

  if (!masterKeySet) {
    return {
      status: 'degraded',
      vaultExists,
      masterKeySet,
      message: 'ARCHONX_MASTER_KEY is not set; vault running in default-key mode.',
    };
  }

  return {
    status: 'degraded',
    vaultExists,
    masterKeySet,
    message: 'Vault file not found at .archonx/vault.bin — run initial vault setup.',
  };
}

// CLI entry point — invoked by the HERMES pre-flight health check:
//   npx ts-node archonx/secrets/vault-client.ts --health
if (require.main === module) {
  const args = process.argv.slice(2);
  if (args.includes('--health')) {
    const result = checkVaultHealth();
    console.log(JSON.stringify(result, null, 2));
    process.exit(result.status === 'error' ? 1 : 0);
  } else {
    console.error(
      'Usage: npx ts-node archonx/secrets/vault-client.ts --health'
    );
    process.exit(1);
  }
}
