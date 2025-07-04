from dateutil.parser import parse
from config.config import get_supabase_client
from exceptions.global_exception import GlobalException


class ViewModelsCore:
    def __init__(self):
        self.client = get_supabase_client()

    def read_farmer_dashboard_view_model(self, farmer_user_profile_id: int):
        try:
            # Check if user profile exists
            user_exists = self.client.table("user_profiles") \
                .select("id") \
                .eq("id", farmer_user_profile_id) \
                .maybe_single() \
                .execute()

            if not user_exists:
                raise GlobalException(
                    f"User profile ID {farmer_user_profile_id} does not exist.", status_code=404)

            # Get latest feed usage
            feed_usage_response = self.client.table("feed_usage_logs").select("*") \
                .eq("farmer_user_profile_id", farmer_user_profile_id) \
                .order("created_at", desc=True).limit(1).execute()

            feed_usage = feed_usage_response.data[0] if feed_usage_response.data else None
            if not feed_usage:
                raise GlobalException(
                    "No feed usage logs found.", status_code=404)

            start_date = feed_usage["start_date"]
            end_date = feed_usage.get("end_date")
            feed_product_id = feed_usage["feed_product_id"]

            # Get feed product info
            feed_product_response = self.client.table("feed_products").select("*") \
                .eq("id", feed_product_id).single().execute()

            feed_product = feed_product_response.data or {}

            # Get farm performance logs during feed usage
            farm_logs_query = self.client.table("farm_performance_logs").select("*") \
                .eq("user_profile_id", farmer_user_profile_id) \
                .gte("created_at", start_date)

            if end_date:
                farm_logs_query = farm_logs_query.lte("created_at", end_date)

            farm_performance_log = farm_logs_query.order(
                "created_at", desc=True).execute()
            logs = farm_performance_log.data or []
            total_logs = len(logs)

            # Calculate growth rate
            growth_data = self.__calculate_growth_rate(logs)
            growth_rate = growth_data["growth_rate"]
            raw_gain_kg = growth_data["raw_gain_kg"]

            # Get farmer ID
            farmer_response = self.client.table("farmers").select("id") \
                .eq("user_profile_id", farmer_user_profile_id) \
                .single().execute()

            if not farmer_response.data:
                raise GlobalException(
                    "Farmer not found for this user profile.", status_code=404)

            farmer_id = farmer_response.data["id"]

            # Get flock size
            flock_size_response = self.client.table("farmer_livestock").select("quantity") \
                .eq("farmer_id", farmer_id).single().execute()

            if not flock_size_response.data:
                raise GlobalException(
                    "Flock size information missing for this farmer.", status_code=404)

            flock_size = flock_size_response.data.get("quantity", 0)
            if not flock_size:
                raise GlobalException(
                    "Flock size is zero or undefined. Cannot compute metrics.", status_code=400)

            total_mortality = sum(
                [log["mortality_count"] for log in logs if log["mortality_count"] is not None])
            mortality_percentage = round(
                (total_mortality / flock_size) * 100, 2)
            survival_rate = (1 - (total_mortality / flock_size))

            latest_log = logs[0] if logs else {}

            # Performance Index calculation
            try:
                average_weight = float(
                    latest_log.get("average_weight_kg", 0.0))
                total_weight_kg = round(
                    sum(float(log["average_weight_kg"]) for log in logs), 3)
                fcr = float(latest_log.get("feed_conversion_ratio", 1.0))
                performance_index = round(
                    ((average_weight * survival_rate) / fcr) * 100, 2)
            except Exception as e:
                raise GlobalException(
                    "Failed to calculate Performance Index.", status_code=500)

            actual_weight = float(latest_log.get(
                "average_weight_kg", 0.0)) if latest_log else 0.0

            # Get target weight from feed_growth_targets
            target_weight_response = self.client.table("feed_growth_targets").select("target_weight_kg") \
                .eq("feed_product_id", feed_product_id).limit(1).single().execute()

            if not target_weight_response.data:
                raise GlobalException(
                    "Target weight data is missing for this feed product.", status_code=404)

            target_weight = float(
                target_weight_response.data["target_weight_kg"])

            latest_per_day = {}
            for log in logs:
                date_str = parse(log["created_at"]).date().isoformat()
                latest_per_day[date_str] = log

            growth_chart_data = [
                {
                    "date": date,
                    "actual_weight": float(log["average_weight_kg"]),
                    "target_weight": target_weight
                }
                for date, log in sorted(latest_per_day.items())
            ]

            recent_records = []
            for log in logs:
                log_date = parse(log["created_at"]).date()
                day_number = (log_date - parse(start_date).date()).days + 1
                recent_records.append({
                    "date": log_date.isoformat(),
                    "day": f"Day {day_number}",
                    "actual_weight": float(log["average_weight_kg"]),
                    "note": log.get("notes", "")
                })

            feed_intake_summary = {
                "eating_well": 0,
                "picky": 0,
                "not_eating": 0
            }
            total_feed_behavior_logs = 0
            behavior_score = 0.0

            recent_feed_records = []
            for log in logs:
                behavior = log.get("feed_intake_status")
                if behavior in feed_intake_summary:
                    feed_intake_summary[behavior] += 1
                    total_feed_behavior_logs += 1

                log_date = parse(log["created_at"])
                recent_feed_records.append({
                    "date": log_date.isoformat(),
                    "feed_intake_status": behavior,
                    "feed_intake_kg": log.get("feed_intake_kg")
                })

            score_weights = {
                "eating_well": 1.0,
                "picky": 0.5,
                "not_eating": 0.0
            }

            if total_feed_behavior_logs > 0:
                weighted_score = sum(
                    feed_intake_summary[k] * score_weights[k] for k in feed_intake_summary)
                behavior_score = round(
                    (weighted_score / total_feed_behavior_logs) * 100, 2)

            dominant_status = max(
                feed_intake_summary, key=feed_intake_summary.get) if total_feed_behavior_logs else None

            # Feed calc log
            calc_resp = (
                self.client
                .table("feed_calculation_logs")
                .select("*")
                .eq("user_profile_id", farmer_user_profile_id)
                .order("created_at", desc=True)
                .limit(1)
                .single()
                .execute()
            )

            if not calc_resp.data:
                raise GlobalException(
                    "No recent feed calculation log found.", status_code=404)

            feed_calc = calc_resp.data

            # Health incidents
            incident_response = (
                self.client.table("health_incidents")
                .select("*")
                .eq("farmer_user_profile_id", farmer_user_profile_id)
                .order("incident_date", desc=True)
                .execute()
            )
            incidents = incident_response.data or []

            sick_count = 0
            mortality_count = 0
            notes_count = 0
            health_score = 100

            recent_issues = []
            for incident in incidents:
                kind = incident["incident_type"]
                affected = incident["affected_count"]
                has_note = bool(incident.get("symptoms")
                                or incident.get("suspected_cause"))

                if kind == "sickness":
                    sick_count += affected
                    health_score -= affected * 2
                elif kind == "mortality":
                    mortality_count += affected
                    health_score -= affected * 4
                if has_note:
                    notes_count += 1
                    health_score -= 1

                recent_issues.append({
                    "date": incident["incident_date"],
                    "incident_type": kind,
                    "affected_count": affected,
                    "symptoms": incident.get("symptoms"),
                    "suspected_cause": incident.get("suspected_cause"),
                    "requires_vet_visit": incident.get("requires_vet_visit"),
                    "feed_info": incident.get("feed_info"),
                    "actions_taken": incident.get("actions_taken"),
                })

            health_score = max(0, min(health_score, 100))

            # Final response
            return {
                "used_feed": {
                    "feed_product_id": feed_product.get("id"),
                    "feed_name": feed_product.get("name"),
                    "feed_stage": feed_product.get("feed_stage"),
                    "feed_goal": feed_product.get("goal"),
                    "age_range_start": feed_product.get("age_range_start"),
                    "age_range_end": feed_product.get("age_range_end"),
                    "start_date": start_date,
                },
                "growth_performance": {
                    "daily_average_growth_rate": growth_rate,
                    "current_fcr": float(logs[0]["feed_conversion_ratio"]) if logs else 0.0,
                    "actual_weight": actual_weight,
                    "target_weight": target_weight,
                    "growth_chart_data": growth_chart_data,
                    "performance_analytics": {
                        "total_logs": total_logs,
                        "total_weight_kg": total_weight_kg,
                        "mortality_count": total_mortality,
                        "mortality_percentage": mortality_percentage,
                        "performance_index": performance_index,
                        "recent_records": recent_records,
                    }
                },
                "feed_calculation_log": {
                    **feed_calc
                },
                "feed_intake_behavior": {
                    "behavior_score": behavior_score,
                    "behavior_status": dominant_status,
                    "summary": feed_intake_summary,
                    "recent_feed_records": recent_feed_records,
                },
                "health_watch": {
                    "health_score": health_score,
                    "issue_summary": {
                        "sick": sick_count,
                        "mortality": mortality_count,
                        "notes": notes_count
                    },
                    "recent_issues": recent_issues
                },
            }

        except GlobalException:
            raise  # Let FastAPI middleware handle it
        except Exception as e:
            raise GlobalException(
                f"Internal Server Error: {e}", status_code=500)

    def __calculate_growth_rate(self, logs: list) -> dict:
        if len(logs) < 2:
            return {
                "growth_rate": 0.0,
                "raw_gain_kg": 0.0
            }

        first_log = logs[-1]
        last_log = logs[0]

        try:
            weight_start = float(first_log["average_weight_kg"])
            weight_end = float(last_log["average_weight_kg"])
            date_start = parse(first_log["created_at"])
            date_end = parse(last_log["created_at"])

            days = (date_end - date_start).days
            if days <= 0:
                return {
                    "growth_rate": 0.0,
                    "raw_gain_kg": 0.0
                }

            return {
                "growth_rate": round((weight_end - weight_start) / days, 3),
                "raw_gain_kg": round((weight_end - weight_start), 3)
            }
        except Exception as e:
            print(f"Error calculating growth rate: {e}")
            return {
                "growth_rate": 0.0,
                "raw_gain_kg": 0.0
            }
