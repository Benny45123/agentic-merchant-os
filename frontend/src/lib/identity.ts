/**
 * Zero-Friction Persistent Omnichannel Identity for Web Shoppers.
 * Automatically generates, retrieves, and persists a unique device identity across sessions.
 */

export interface ShopperIdentity {
  buyerId: string;
  displayName: string;
  channel: "web";
}

function detectPlatformName(): string {
  if (typeof window === "undefined") return "Web Shopper";
  const ua = navigator.userAgent;
  let browser = "Browser";
  let os = "Device";

  if (ua.includes("Firefox")) browser = "Firefox";
  else if (ua.includes("Edg")) browser = "Edge";
  else if (ua.includes("Chrome")) browser = "Chrome";
  else if (ua.includes("Safari")) browser = "Safari";

  if (ua.includes("iPhone")) os = "iPhone";
  else if (ua.includes("iPad")) os = "iPad";
  else if (ua.includes("Macintosh") || ua.includes("Mac OS")) os = "macOS";
  else if (ua.includes("Android")) os = "Android";
  else if (ua.includes("Windows")) os = "Windows";
  else if (ua.includes("Linux")) os = "Linux";

  return `Shopper (${browser} • ${os})`;
}

export function getOrCreateShopperIdentity(): ShopperIdentity {
  if (typeof window === "undefined") {
    return { buyerId: "b_001", displayName: "Demo Shopper", channel: "web" };
  }

  // 1. Check localStorage
  const storedId = localStorage.getItem("amos_shopper_id");
  const storedName = localStorage.getItem("amos_shopper_name");

  if (storedId && storedId.trim()) {
    return {
      buyerId: storedId.trim(),
      displayName: storedName || detectPlatformName(),
      channel: "web",
    };
  }

  // 2. Generate new persistent device ID
  const randomSuffix = Math.random().toString(16).substring(2, 8);
  const newBuyerId = `b_dev_${randomSuffix}`;
  const defaultName = detectPlatformName();

  try {
    localStorage.setItem("amos_shopper_id", newBuyerId);
    localStorage.setItem("amos_shopper_name", defaultName);
    // Also store in 1-year persistent cookie
    document.cookie = `amos_buyer_id=${newBuyerId}; max-age=31536000; path=/; SameSite=Lax`;
  } catch (e) {
    console.warn("Storage write failed:", e);
  }

  return {
    buyerId: newBuyerId,
    displayName: defaultName,
    channel: "web",
  };
}

export function updateShopperName(newName: string): void {
  if (typeof window === "undefined") return;
  const clean = newName.trim();
  if (clean) {
    localStorage.setItem("amos_shopper_name", clean);
  }
}
