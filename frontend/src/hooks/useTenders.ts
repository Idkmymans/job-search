import { useState, useEffect } from 'react';
import { supabase } from '../lib/supabase';
import { Tender, TenderFilter } from '../types';

export const useTenders = () => {
  const [tenders, setTenders] = useState<Tender[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchTenders();
  }, []);

  const fetchTenders = async (filter?: TenderFilter, markedRelevant?: boolean) => {
    try {
      setLoading(true);
      setError(null);
      let query = supabase.from('tenders').select('*');

      if (markedRelevant !== undefined) {
        query = query.eq('marked_relevant', markedRelevant);
      }

      if (filter?.keyword) {
        query = query.or(
          `title.ilike.%${filter.keyword}%,ifb_no.ilike.%${filter.keyword}%,organization.ilike.%${filter.keyword}%`
        );
      }

      if (filter?.organization && filter.organization.length > 0) {
        query = query.in('organization', filter.organization);
      }

      if (filter?.procurement_type && filter.procurement_type.length > 0) {
        query = query.in('procurement_type', filter.procurement_type);
      }

      if (filter?.date_from) {
        query = query.gte('deadline', filter.date_from);
      }

      if (filter?.date_to) {
        query = query.lte('deadline', filter.date_to);
      }

      if (filter?.days_left_min !== undefined) {
        query = query.gte('days_left', filter.days_left_min);
      }

      if (filter?.days_left_max !== undefined) {
        query = query.lte('days_left', filter.days_left_max);
      }

      if (filter?.province && filter.province.length > 0) {
        query = query.in('province', filter.province);
      }

      if (filter?.source && filter.source.length > 0) {
        query = query.in('source', filter.source);
      }

      const { data, error: fetchError } = await query.order('deadline', { ascending: true });

      if (fetchError) throw fetchError;
      setTenders(data || []);
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Failed to fetch tenders';
      setError(message);
    } finally {
      setLoading(false);
    }
  };

  const addTender = async (tender: Omit<Tender, 'id' | 'created_at' | 'updated_at'>) => {
    try {
      const { data, error: insertError } = await supabase
        .from('tenders')
        .insert([tender])
        .select();

      if (insertError) throw insertError;
      if (data) setTenders([...tenders, data[0]]);
      return data?.[0];
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Failed to add tender';
      setError(message);
      throw err;
    }
  };

  const updateTender = async (id: string, updates: Partial<Tender>) => {
    try {
      const { data, error: updateError } = await supabase
        .from('tenders')
        .update(updates)
        .eq('id', id)
        .select();

      if (updateError) throw updateError;
      if (data) {
        setTenders(tenders.map((t) => (t.id === id ? data[0] : t)));
      }
      return data?.[0];
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Failed to update tender';
      setError(message);
      throw err;
    }
  };

  const markRelevant = async (id: string, marked: boolean) => {
    return updateTender(id, { marked_relevant: marked });
  };

  const deleteTenders = async (ids: string[]) => {
    try {
      const { error: deleteError } = await supabase
        .from('tenders')
        .delete()
        .in('id', ids);

      if (deleteError) throw deleteError;
      setTenders(tenders.filter((t) => !ids.includes(t.id)));
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Failed to delete tenders';
      setError(message);
      throw err;
    }
  };

  const clearAllTenders = async () => {
    try {
      const { error: deleteError } = await supabase
        .from('tenders')
        .delete()
        .gte('created_at', '1970-01-01');

      if (deleteError) throw deleteError;
      setTenders([]);
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Failed to clear tenders';
      setError(message);
      throw err;
    }
  };

  return {
    tenders,
    loading,
    error,
    fetchTenders,
    addTender,
    updateTender,
    markRelevant,
    deleteTenders,
    clearAllTenders,
  };
};
