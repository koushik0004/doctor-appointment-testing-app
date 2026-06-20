"use client";

import * as React from "react";

import { getRecommendedDoctors } from "@/features/appointments/api";
import type { RecommendedDoctorsResponse } from "@/features/appointments/types";
import { ApiError } from "@/lib/api-client";

type RecommendedDoctorsState = {
  data: RecommendedDoctorsResponse | null;
  error: string | null;
  isLoading: boolean;
};

const initialState: RecommendedDoctorsState = {
  data: null,
  error: null,
  isLoading: false,
};

export function useRecommendedDoctors(appointmentId: number | null) {
  const abortControllerRef = React.useRef<AbortController | null>(null);
  const [state, setState] = React.useState<RecommendedDoctorsState>(initialState);
  const [reloadKey, setReloadKey] = React.useState(0);

  React.useEffect(() => {
    return () => {
      abortControllerRef.current?.abort();
    };
  }, []);

  React.useEffect(() => {
    abortControllerRef.current?.abort();
    abortControllerRef.current = null;

    if (appointmentId === null) {
      setState(initialState);
      return;
    }

    const controller = new AbortController();
    abortControllerRef.current = controller;
    const selectedAppointmentId = appointmentId;

    setState((current) => ({
      ...current,
      isLoading: true,
      error: null,
    }));

    let isActive = true;

    async function loadRecommendedDoctors() {
      try {
        const response = await getRecommendedDoctors(selectedAppointmentId, {
          signal: controller.signal,
        });

        if (!isActive || controller.signal.aborted) {
          return;
        }

        setState({
          data: response,
          error: null,
          isLoading: false,
        });
      } catch (error) {
        if (!isActive || controller.signal.aborted) {
          return;
        }

        setState({
          data: null,
          error:
            error instanceof ApiError
              ? error.message
              : error instanceof Error
                ? error.message
                : "Unable to load recommended doctors.",
          isLoading: false,
        });
      }
    }

    loadRecommendedDoctors();

    return () => {
      isActive = false;
      controller.abort();
    };
  }, [appointmentId, reloadKey]);

  const refetch = React.useCallback(() => {
    setReloadKey((value) => value + 1);
  }, []);

  return {
    data: state.data,
    error: state.error,
    isLoading: state.isLoading,
    refetch,
  };
}
