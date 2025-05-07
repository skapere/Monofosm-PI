export interface Phone {
    modele: string;
    marque: string;
    ram: string;
    stockage: string;
    couleur: string;
    options: string;
    reference_global: string;
    reference_detail: string;
    ad_title: string;
    ad_url: string[];
    shop: string[];
    ad_stocks: string[];
    max_price: number;
    min_price: number;
    date_scrapy: Date[];
    all_prices: number[];
    image: string;
}
