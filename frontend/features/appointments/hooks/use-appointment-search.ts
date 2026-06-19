"use client";

import * as React from "react";

import { ApiError } from "@/lib/api-client";
import {
  searchAppointments as searchAppointmentsApi,
} from "@/features/appointments/api";
import type {
  AppointmentSearchQuery,
  AppointmentSearchResponse,
} from "@/features/appointments/types";

type SearchState = {
  data: AppointmentSearchResponse | null;
  error: string | null;
  isLoading: boolean;
  hasSearched: boolean;
};

const initialState: SearchState = {
  data: null,
  error: null,
  isLoading: false,
  hasSearched: false,
};

export function useAppointmentSearch() {
  const abortControllerRef = React.useRef<AbortController | null>(null);
  const [state, setState] = React.useState<SearchState>(initialState);

  React.useEffect(() => {
    return () => {
      abortControllerRef.current?.abort();
    };
  }, []);

  const resetSearch = React.useCallback(() => {
    abortControllerRef.current?.abort();
    abortControllerRef.current = null;
    setState(initialState);
  }, []);

  const search = React.useCallback(async (query: AppointmentSearchQuery) => {
    abortControllerRef.current?.abort();

    const controller = new AbortController();
    abortControllerRef.current = controller;

    setState((current) => ({
      ...current,
      isLoading: true,
      error: null,
      hasSearched: true,
    }));

    try {
      const response = await searchAppointmentsApi(query, {
        signal: controller.signal,
      });

      if (controller.signal.aborted) {
        return null;
      }

      setState({
        data: response,
        error: null,
        isLoading: false,
        hasSearched: true,
      });

      return response;
    } catch (error) {
      if (controller.signal.aborted) {
        return null;
      }

      const message =
        error instanceof ApiError
          ? error.message
          : error instanceof Error
            ? error.message
            : "Unable to search appointments.";

      setState({
        data: null,
        error: message,
        isLoading: false,
        hasSearched: true,
      });

      return null;
    }
  }, []);

  return {
    data: state.data,
    error: state.error,
    hasSearched: state.hasSearched,
    isLoading: state.isLoading,
    resetSearch,
    search,
  };
}
