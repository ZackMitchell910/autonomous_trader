// src/utils/getTier.js
import { Connection, PublicKey } from '@solana/web3.js';
import { getAccount, getAssociatedTokenAddress, getMint } from '@solana/spl-token';

// Spark token mint address
const SPARK_TOKEN_MINT = new PublicKey('53mTqqc1GFKiLdG9eM282FYFde6muDxqa5mppGEmC8Rm');

// Fetch the user's Spark token balance
export const getSparkBalance = async (publicKey) => {
  const connection = new Connection('https://api.mainnet-beta.solana.com');
  try {
    const tokenAccount = await getAssociatedTokenAddress(SPARK_TOKEN_MINT, new PublicKey(publicKey));
    const accountInfo = await getAccount(connection, tokenAccount);
    return accountInfo.amount; // Returns BigInt representing balance in smallest unit
  } catch (err) {
    console.error('Error fetching balance:', err);
    return BigInt(0);
  }
};

// Determine the user's tier based on balance and decimals
export const determineTier = (balance, decimals) => {
  const divisor = BigInt(10) ** BigInt(decimals);
  const wholeTokens = balance / divisor; // Convert balance to whole tokens

  if (wholeTokens >= BigInt(30000000)) return 'Premium';    // Tier 3: ≥ 30M tokens
  if (wholeTokens >= BigInt(10000000)) return 'Advanced';   // Tier 2: ≥ 10M tokens
  if (wholeTokens >= BigInt(4000000)) return 'Basic';       // Tier 1: ≥ 4M tokens
  return 'Basic';                                           // Default for < 4M tokens
};