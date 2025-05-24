import axios from "@/lib/axios";
import { useQuery, useMutation } from "react-query";

interface TenderForm {
  title: string;
  description: string;
  deadline?: string;
}

interface BidForm {
  tender: number;
  amount: string;
  message?: string;
}

export const useTenders = () =>
  useQuery(["tenders"], () => axios.get("/api/core/tenders/").then(r => r.data));

export const useCreateTender = () =>
  useMutation((payload: TenderForm) =>
    axios.post("/api/core/tenders/", payload));

export const useBids = (tenderId: number) =>
  useQuery(["bids", tenderId], () =>
    axios.get(`/api/core/bids/?tender=${tenderId}`).then(r => r.data));

export const useCreateBid = () =>
  useMutation((payload: BidForm) =>
    axios.post("/api/core/bids/", payload)); 