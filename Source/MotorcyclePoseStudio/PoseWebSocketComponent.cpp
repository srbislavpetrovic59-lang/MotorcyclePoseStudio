#include "PoseWebSocketComponent.h"

#include "WebSocketsModule.h"
#include "Modules/ModuleManager.h"
#include "Dom/JsonObject.h"
#include "Serialization/JsonReader.h"
#include "Serialization/JsonSerializer.h"


UPoseWebSocketComponent::UPoseWebSocketComponent()
{
    PrimaryComponentTick.bCanEverTick = false;
}


void UPoseWebSocketComponent::BeginPlay()
{
    Super::BeginPlay();

    Connect();
}


void UPoseWebSocketComponent::Connect()
{
    FModuleManager::LoadModuleChecked<FWebSocketsModule>("WebSockets");

    WebSocket = FWebSocketsModule::Get().CreateWebSocket(
        TEXT("ws://127.0.0.1:8765")
    );

    WebSocket->OnConnected().AddUObject(
        this,
        &UPoseWebSocketComponent::HandleConnected
    );

    WebSocket->OnConnectionError().AddUObject(
        this,
        &UPoseWebSocketComponent::HandleConnectionError
    );

    WebSocket->OnClosed().AddUObject(
        this,
        &UPoseWebSocketComponent::HandleClosed
    );

    WebSocket->OnMessage().AddUObject(
        this,
        &UPoseWebSocketComponent::HandleMessage
    );

    UE_LOG(
        LogTemp,
        Display,
        TEXT("Pose WebSocket: connecting to ws://127.0.0.1:8765")
    );

    WebSocket->Connect();
}


void UPoseWebSocketComponent::HandleConnected()
{
    UE_LOG(
        LogTemp,
        Display,
        TEXT("Pose WebSocket: connected")
    );
}


void UPoseWebSocketComponent::HandleConnectionError(
    const FString& Error
)
{
    UE_LOG(
        LogTemp,
        Error,
        TEXT("Pose WebSocket connection error: %s"),
        *Error
    );
}


void UPoseWebSocketComponent::HandleClosed(
    int32 StatusCode,
    const FString& Reason,
    bool bWasClean
)
{
    if (StatusCode == 1000)
    {
        UE_LOG(
            LogTemp,
            Display,
            TEXT("Pose WebSocket closed normally.")
        );
        return;
    }

    UE_LOG(
        LogTemp,
        Warning,
        TEXT(
            "Pose WebSocket closed. Code: %d, Reason: %s"
        ),
        StatusCode,
        *Reason
    );
}


void UPoseWebSocketComponent::HandleMessage(
    const FString& Message
)
{
    FRiderState RiderState;

    if (!ParseRiderState(Message, RiderState))
    {
        UE_LOG(
            LogTemp,
            Warning,
            TEXT("Pose WebSocket received invalid RiderState JSON.")
        );
        return;
    }
    
    if (
        bHasPreviousFrontBrakeState
        && RiderState.bHasFrontBrakeProgress
        )
    {
        if (
            !bPreviousFrontBrakeActive
            && RiderState.bFrontBrakeActive
            )
        {
            UE_LOG(
                LogTemp,
                Display,
                TEXT("Front brake APPLIED")
            );

            OnFrontBrakeApplied.Broadcast();
        }
        else if (
            bPreviousFrontBrakeActive
            && !RiderState.bFrontBrakeActive
            )
        {
            UE_LOG(
                LogTemp,
                Display,
                TEXT("Front brake RELEASED")
            );

            OnFrontBrakeReleased.Broadcast();
        }
    }

    if (RiderState.bHasFrontBrakeProgress)
    {
        bPreviousFrontBrakeActive =
            RiderState.bFrontBrakeActive;

        bHasPreviousFrontBrakeState = true;

        bFrontBrakeActive =
            RiderState.bFrontBrakeActive;
    }

    if (RiderState.bHasThrottleProgress)
    {
        UE_LOG(
            LogTemp,
            Display,
            TEXT("ThrottleProgress: %.2f"),
            RiderState.ThrottleProgress
        );
    }
    else
    {
        UE_LOG(
            LogTemp,
            Display,
            TEXT("ThrottleProgress: INVALID")
        );
    }

    if (RiderState.bHasClutchProgress)
    {
        UE_LOG(
            LogTemp,
            Display,
            TEXT("ClutchProgress: %.2f, FrictionZone: %s"),
            RiderState.ClutchProgress,
            RiderState.bClutchInFrictionZone
            ? TEXT("true")
            : TEXT("false")
        );
    }
    else
    {
        UE_LOG(
            LogTemp,
            Display,
            TEXT("ClutchProgress: INVALID, FrictionZone: false")
        );
    }
    if (RiderState.bHasFrontBrakeProgress)
    {
        UE_LOG(
            LogTemp,
            Display,
            TEXT("FrontBrakeProgress: %.2f, Active: %s"),
            RiderState.FrontBrakeProgress,
            RiderState.bFrontBrakeActive
            ? TEXT("true")
            : TEXT("false")
        );
    }
    else
    {
        UE_LOG(
            LogTemp,
            Display,
            TEXT("FrontBrakeProgress: INVALID, Active: false")
        );
    }
    UE_LOG(
        LogTemp,
        Display,
        TEXT(
            "RiderState: head %.1f / %.1f, elbows %.1f / %.1f, "
            "knees %.1f / %.1f, "
            "feet %.1f / %.1f, "
            "torso %.1f, confidence %.2f, "
			"ClutchProgress: %.2f, FrictionZone: %s"
        ),
        RiderState.HeadRoll,
        RiderState.HeadYawRatio,
        RiderState.LeftElbow,
        RiderState.RightElbow,
        RiderState.LeftKnee,
        RiderState.RightKnee,
        RiderState.LeftFoot,
		RiderState.RightFoot,
        RiderState.TorsoAngle,
        RiderState.PoseConfidence,
        RiderState.ClutchProgress,
		RiderState.bClutchInFrictionZone ? TEXT("true")
        : TEXT("false")
    );

}

void UPoseWebSocketComponent::TickComponent(
    float DeltaTime,
    ELevelTick TickType,
    FActorComponentTickFunction* ThisTickFunction
)
{
    Super::TickComponent(
        DeltaTime,
        TickType,
        ThisTickFunction
    );
}

bool UPoseWebSocketComponent::ParseRiderState(
    const FString& Message,
    FRiderState& OutRiderState
) const
{
    TSharedPtr<FJsonObject> JsonObject;

    const TSharedRef<TJsonReader<>> Reader =
        TJsonReaderFactory<>::Create(Message);

    if (!FJsonSerializer::Deserialize(Reader, JsonObject) ||
        !JsonObject.IsValid())
    {
        return false;
    }

    double Value = 0.0;
    if (!JsonObject->TryGetNumberField(TEXT("head_roll"), Value))
    {
        return false;
	}
	OutRiderState.HeadRoll = static_cast<float>(Value);

    if (!JsonObject->TryGetNumberField(TEXT("head_yaw_ratio"), Value))
    {
        return false;
    }

    OutRiderState.HeadYawRatio = static_cast<float>(Value);

    if (!JsonObject->TryGetNumberField(TEXT("left_elbow_angle"), Value))
    {
        return false;
    }
    OutRiderState.LeftElbow = static_cast<float>(Value);

    if (!JsonObject->TryGetNumberField(TEXT("right_elbow_angle"), Value))
    {
        return false;
    }
    OutRiderState.RightElbow = static_cast<float>(Value);

    if (JsonObject->TryGetNumberField(TEXT("left_knee_angle"), Value))
    {
        OutRiderState.LeftKnee = static_cast<float>(Value);
    }

    if (JsonObject->TryGetNumberField(TEXT("right_knee_angle"), Value))
    {
        OutRiderState.RightKnee = static_cast<float>(Value);
    }

    if (JsonObject->TryGetNumberField(TEXT("left_foot_angle"), Value))
    {
        OutRiderState.LeftFoot = static_cast<float>(Value);
	}

    if (JsonObject->TryGetNumberField(TEXT("right_foot_angle"), Value))
    {
        OutRiderState.RightFoot = static_cast<float>(Value);
    }

    if (JsonObject->TryGetNumberField(TEXT("torso_angle"), Value))
    {
        OutRiderState.TorsoAngle = static_cast<float>(Value);
    }

    if (!JsonObject->TryGetNumberField(TEXT("pose_confidence"), Value))
    {
        return false;
    }
    OutRiderState.PoseConfidence = static_cast<float>(Value);

    if (JsonObject->TryGetNumberField(
        TEXT("clutch_progress"),
        Value))
    {
        OutRiderState.ClutchProgress =
            static_cast<float>(Value);

        OutRiderState.bHasClutchProgress = true;
    }
    else
    {
        OutRiderState.ClutchProgress = 0.0f;
        OutRiderState.bHasClutchProgress = false;
    }
    bool bValue = false;

    if (JsonObject->TryGetBoolField(
        TEXT("clutch_in_friction_zone"),
        bValue))
    {
        OutRiderState.bClutchInFrictionZone = bValue;
    }
    else
    {
        OutRiderState.bClutchInFrictionZone = false;
    }
    if (JsonObject->TryGetNumberField(
        TEXT("front_brake_progress"),
        Value))
    {
        OutRiderState.FrontBrakeProgress =
            static_cast<float>(Value);

        OutRiderState.bHasFrontBrakeProgress = true;
    }
    else
    {
        OutRiderState.FrontBrakeProgress = 0.0f;
        OutRiderState.bHasFrontBrakeProgress = false;
    }
    bool bFrontBrakeValue = false;

    if (JsonObject->TryGetBoolField(
        TEXT("front_brake_active"),
        bFrontBrakeValue))
    {
        OutRiderState.bFrontBrakeActive =
            bFrontBrakeValue;
    }
    else
    {
        OutRiderState.bFrontBrakeActive = false;
    }
    if (JsonObject->TryGetNumberField(
        TEXT("throttle_progress"),
        Value
    ))
    {
        OutRiderState.ThrottleProgress =
            static_cast<float>(Value);

        OutRiderState.bHasThrottleProgress = true;
    }
    else
    {
        OutRiderState.ThrottleProgress = 0.0f;
        OutRiderState.bHasThrottleProgress = false;
    }
    return true;
}