import {PriminiPhone} from "./priminiphone.model";
export interface ItemCart {
  phone: PriminiPhone;
  quantity: number;
}

export interface Cart {
  reference: string;
  employee: string;
  phones: ItemCart[];
  total: number;
  status: string;
}
