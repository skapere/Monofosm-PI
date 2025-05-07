export interface Filters {
    max_price: number;
    min_price: number;
    ram: string[];
    stockage: string[];
    stocks: Stocks[];
    couleur: Couleur[];
    shop: Shop[];
    marque: Marque[];
}

export interface Couleur {
  name: string;
  count: number;
}
export interface Stocks {
  name: string;
  count: number;
}
export interface Shop {
  name: string;
  count: number;
}
export interface Marque {
  name: string;
  count: number;
}
