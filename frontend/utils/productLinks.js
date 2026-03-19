const VENDOR_BASE_URLS = {
    'Pepperfry': 'https://www.pepperfry.com/',
    'Urban Ladder': 'https://www.urbanladder.com/',
    'IKEA': 'https://www.ikea.com/in/en/',
    'Asian Paints': 'https://www.asianpaints.com/',
    'Amazon India': 'https://www.amazon.in/',
    'Jaipur Rugs': 'https://www.jaipurtugs.com/',
    'Kapoor Lights': 'https://www.amazon.in/',
};

export function getProductShopUrl(product) {
    if (product.affiliateLink && product.affiliateLink !== '#') {
        return product.affiliateLink;
    }
    return VENDOR_BASE_URLS[product.vendor] || '#';
}

export function openProductInNewTab(product) {
    const url = getProductShopUrl(product);
    if (url !== '#') window.open(url, '_blank', 'noopener,noreferrer');
}
