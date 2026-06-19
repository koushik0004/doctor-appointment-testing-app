"use client";

import * as React from "react";

import { ApiError } from "@/lib/api-client";
import { getAppointmentDetails } from "@/features/appointments/api";
import type { AppointmentDetailsResponse } from "@/features/appointments/types";

type AppointmentDetailsState = {
  data: AppointmentDetailsResponse | null;
  error: string | null;
  isLoading: boolean;
};

const initialState: AppointmentDetailsState = {
  data: null,
  error: null,
  isLoading: false,
};

export function useAppointmentDetails(appointmentId: number | null) {
  const abortControllerRef = React.useRef<AbortController | null>(null);
  const [state, setState] = React.useState<AppointmentDetailsState>(initialState);
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

    const selectedAppointmentId = appointmentId;
    const controller = new AbortController();
    abortControllerRef.current = controller;

    setState((current) => ({
      ...current,
      isLoading: true,
      error: null,
    }));

    let isActive = true;

    async function loadAppointmentDetails() {
      try {
        const response = await getAppointmentDetails(selectedAppointmentId, {
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
                : "Unable to load appointment details.",
          isLoading: false,
        });
      }
    }

    loadAppointmentDetails();

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
