import { Connection, PublicKey } from '@solana/web3.js';
import { getAccount, getAssociatedTokenAddress, getMint } from '@solana/spl-token';

const SPARK_TOKEN_MINT = new PublicKey('53mTqqc1GFKiLdG9eM282FYFde6muDxqa5mppGEmC8Rm');

export const getSparkBalance = async (publicKey) => {
  const connection = new Connection('https://api.mainnet-beta.solana.com');
  try {
    const tokenAccount = await getAssociatedTokenAddress(SPARK_TOKEN_MINT, new PublicKey(publicKey));
    const accountInfo = await getAccount(connection, tokenAccount);
    return accountInfo.amount; // Returns BigInt
  } catch (err) {
    console.error('Error fetching balance:', err);
    return BigInt(0);
  }
};

export const determineTier = (wholeTokens) => {
  if (wholeTokens >= BigInt(30000000)) return 'Tier 3';
  if (wholeTokens >= BigInt(10000000)) return 'Tier 2';
  if (wholeTokens >= BigInt(4000000)) return 'Tier 1';
  return 'None';
};